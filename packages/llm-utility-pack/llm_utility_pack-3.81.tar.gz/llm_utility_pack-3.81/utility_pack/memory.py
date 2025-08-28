from utility_pack.vector_storage_helper import LmdbStorage
from utility_pack.embeddings import extract_embeddings
from utility_pack.vector_storage import VectorDB
from utility_pack.text import compress_text
from utility_pack.llm import rerank
import uuid, pymongo, time, datetime

class Memory:
    def __init__(
            self,
            mongo_uri: str,
            mongo_database: str,
            mongo_collection_vectordb: str,
            mongo_collection_conversation_data: str,
            override_vector_storage = None,
            override_text_storage = None
        ):
        if not override_text_storage:
            override_text_storage = LmdbStorage("memory_text_storage")
        if not override_vector_storage:
            override_vector_storage = LmdbStorage("memory_vector_storage")

        self.vectordb = VectorDB(
            mongo_uri = mongo_uri,
            mongo_database = mongo_database,
            mongo_collection = mongo_collection_vectordb,
            vector_storage = override_vector_storage,
            text_storage = override_text_storage
        )
        self.semantic_vectors_storage = override_vector_storage
        self.semantic_texts_storage = override_text_storage

        self.mongo_database = mongo_database
        self.mongo_collection_conversation_data = mongo_collection_conversation_data
        self.mongo_collection_vectordb = mongo_collection_vectordb

        self.connection = pymongo.MongoClient(mongo_uri)
        self.conversation_collection = self.connection[mongo_database][mongo_collection_conversation_data]
            
    def store_embeddings(self, sentences: list, session_id: str, message_id: str, type: str):
        unique_ids = [str(uuid.uuid4()) for _ in range(len(sentences))]
        embeddings = [extract_embeddings(sentence) for sentence in sentences]
        metadatas = [
            {
                'text': sentence,
                'session_id': session_id,
                'message_id': message_id,
                'type': type
            }
            for sentence in sentences
        ]

        self.vectordb.store_embeddings_batch(
            unique_ids = unique_ids,
            embeddings = embeddings,
            metadata_dicts = metadatas,
            text_field = 'text'
        )

    def memorize(self, question, answer, session_id=None):
        if session_id is None:
            session_id = str(uuid.uuid4())

        question_id = str(uuid.uuid4())
        question_summary = compress_text(question, target_token_count=300)

        answer_id = str(uuid.uuid4())
        answer_summary = compress_text(answer, target_token_count=300)

        self.conversation_collection.insert_one({
            'session_id': session_id,
            'message_id': question_id,
            'question': question,
            'question_summary': question_summary,
            'timestamp': datetime.datetime.now(datetime.timezone.utc)
        })

        # Sleep for 10ms so the answer is inserted after the question
        time.sleep(0.01)

        self.conversation_collection.insert_one({
            'session_id': session_id,
            'message_id': answer_id,
            'answer': answer,
            'answer_summary': answer_summary,
            'timestamp': datetime.datetime.now(datetime.timezone.utc)
        })

        self.store_embeddings([question_summary], session_id, question_id, 'question')
        self.store_embeddings([answer_summary], session_id, answer_id, 'answer')

        return session_id, question_id, answer_id

    def get_last_interactions(self, session_id, num_chats=4, recent_first=True):
        chats = list(self.conversation_collection.find(
            {'session_id': session_id},
            sort = [('timestamp', -1 if recent_first else 1)],
            limit = num_chats
        ))

        # Convert to dictionary format
        columns = ['session_id', 'message_id', 'question', 'question_summary', 'answer', 'answer_summary', 'timestamp']

        # Ensure all items contains all columns, if not, fill with None
        for chat in chats:
            for column in columns:
                if column not in chat:
                    chat[column] = None

        return chats

    def remember(self, session_id, new_prompt, recent_interaction_count = 4):
        """
        Fetches relevant information from the database based on the new prompt.
        """
        # Retrieve the N most recent pairs of questions and answers
        last_n_messages = self.get_last_interactions(session_id, recent_interaction_count)
        last_n_messages_ids = [ m['message_id'] for m in last_n_messages ]

        # Get embeddings for the incoming prompt
        prompt_embedding = extract_embeddings(new_prompt)

        # Search in vector database for the most similar question
        # (Excluding the last "N" messages, as they are fetched directly from the database)
        _, _, metadatas = self.vectordb.find_most_similar(
            embedding = prompt_embedding,
            filters = {'session_id': session_id},
            output_fields = 'all',
            k = 20,
            use_find_one = False
        )
        if not metadatas:
            return {
                "chat_turns": [],
                "context_memory": [],
                "suggested_context": ""
            }
        
        ranked_results = rerank(
            question = new_prompt,
            passages = [ m['text'] for m in metadatas ]
        )
        ranked_texts = [ rt[0] for rt in ranked_results ]
        ranked_texts = ranked_texts[:10]
        metadatas = [ m for m in metadatas if m['text'] in ranked_texts ]
        metadatas = [ m for m in metadatas if m['message_id'] not in last_n_messages_ids ][:2]

        suggested_context = ""
        if len(metadatas) > 0:
            for metadata in metadatas:
                suggested_context += f"Previous context ({'prompt' if metadata['type'] == 'question' else 'answer'}): {metadata['text']}\n"

        suggested_context += "\n"

        if len(last_n_messages) > 0:
            last_n_messages.reverse()
            for message in last_n_messages:
                if 'question' in message and bool(message['question']):
                    suggested_context += f"Previous prompt: {message['question']}\n"
                else:
                    suggested_context += f"Previous answer: {message['answer']}\n"
        
        # Create chat_turns based on recent interactions
        chat_turns = []
        for message in last_n_messages:
            if 'question' in message and bool(message['question']):
                chat_turns.append({
                    "role": "user",
                    "content": message['question']
                })
            elif 'answer' in message and bool(message['answer']):
                chat_turns.append({
                    "role": "assistant",
                    "content": message['answer']
                })

        # Return the context metadata
        return {
            "chat_turns": last_n_messages,
            "context_memory": metadatas,
            "suggested_context": suggested_context.strip()
        }

    def delete_session_from_vector_db(self, session_id):
        self.vectordb.delete_embeddings_by_metadata({'session_id': session_id})

    def delete_message_from_vector_db(self, session_id, message_id):
        self.vectordb.delete_embeddings_by_metadata({'session_id': session_id, 'message_id': message_id})

    def forget_session(self, session_id):
        self.conversation_collection.delete_many({'session_id': session_id})

        # Delete from the vector database
        self.delete_session_from_vector_db(session_id)
    
    def forget_message(self, session_id, message_id):
        self.conversation_collection.delete_one({'session_id': session_id, 'message_id': message_id})

        # Delete from the vector database
        self.delete_message_from_vector_db(session_id, message_id)

    def list_messages(self, session_id, count = False, page = 1, limit = 20, recent_first = True):
        if count:
            return self.conversation_collection.count_documents({'session_id': session_id})
        else:
            offset = (page - 1) * limit
            order = -1 if recent_first else 1
            messages = list(self.conversation_collection.find(
                {'session_id': session_id},
                sort = [('timestamp', order)],
                limit = limit,
                skip = offset
            ))

            return messages
