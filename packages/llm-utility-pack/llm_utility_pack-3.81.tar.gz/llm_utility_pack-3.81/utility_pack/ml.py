from utility_pack.embeddings import EmbeddingType, extract_embeddings
from sklearn.preprocessing import KBinsDiscretizer, OrdinalEncoder, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from multiprocessing import Pool, cpu_count
from scipy.sparse import csr_matrix
from itertools import combinations
import copy, prince, cloudpickle
from prophet import Prophet
from typing import List
import pandas as pd
import numpy as np

def timeseries_forecast(dates: list, values: list, num_forecast_periods: int = 30):
    """
    Creates a forecast using the Prophet model.
    """
    df = pd.DataFrame({
        'ds': dates,
        'y': values
    })

    # Initialize the Prophet model
    model = Prophet()

    # Fit the model
    model.fit(df)

    # Create future dataframe
    future = model.make_future_dataframe(periods=num_forecast_periods)

    # Make predictions
    forecast = model.predict(future)

    input_count = len(dates)

    # Remove the first "input_count" rows from the forecast dataframe
    forecast = forecast[input_count:]

    return forecast['yhat'].tolist()

def has_decimals(x, min_decimals=4):
    decimal_part = str(x).split('.')[-1]
    return len(decimal_part) >= min_decimals

def find_high_correlation_features(df, categorical_columns, ignore_columns, threshold=0.9):
    df_copy = df.copy(deep=True)
    for col in ignore_columns:
        if col in df_copy.columns:
            df_copy.drop(col, axis=1, inplace=True)

    # Encode categorical columns
    df_copy[categorical_columns] = OrdinalEncoder().fit_transform(df_copy[categorical_columns])

    corr_matrix = df_copy.corr(numeric_only=True).abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

    return [column for column in upper.columns if any(upper[column] > threshold)]

def identify_numeric_and_categoric_columns(df: pd.DataFrame):
    ignore_columns = []
    id_column_threshold = 0.9
    
    zip_code_possible_cols = ['ZIPCODE', 'ZIP-CODE', 'ZIP_CODE']

    # Identify ID columns based on the proportion of unique values to total rows and float columns with decimals
    for col in df.columns:
        if df[col].nunique() / len(df) > id_column_threshold:
            if df[col].dtype == np.float64 and not df[col].apply(has_decimals).all():
                continue
            ignore_columns.append(col)
        
        # Check if any of the zip code columns could be inside the column string
        if any([zip_code_col in col.upper() for zip_code_col in zip_code_possible_cols]):
            ignore_columns.append(col)
    
    ignore_columns = list(set(ignore_columns))

    # Identify numerical and categorical columns
    numerical_columns = list(df.select_dtypes(include=[np.number]).columns.difference(ignore_columns))
    categorical_columns = list(df.select_dtypes(include=['object', 'category']).columns.difference(ignore_columns))

    # Define threshold for considering numerical columns as categorical
    unique_value_threshold = 15
    discard_col_unique_threshold_percentage = 0.4

    total_df_count = len(df)

    # Check if numerical columns with low unique values should be considered as categorical
    for col in copy.deepcopy(numerical_columns):
        col_unique_count = df[col].nunique()

        if col_unique_count <= unique_value_threshold:
            if col_unique_count == 0:
                col_unique_count = 1
            if (total_df_count / col_unique_count) >= discard_col_unique_threshold_percentage:
                # Amount of unique categorical values is over 90% of dataset diversity
                # Discard
                numerical_columns.remove(col)
            else:
                print(f"Column {col} has {col_unique_count} unique values and will be considered as categorical.")
                categorical_columns.append(col)
                numerical_columns.remove(col)
    
    for col in copy.deepcopy(categorical_columns):
        col_unique_count = df[col].nunique()

        if col_unique_count >= unique_value_threshold:
            if (col_unique_count / total_df_count) >= discard_col_unique_threshold_percentage:
                # Amount of unique categorical values is over 90% of dataset diversity
                # Discard
                categorical_columns.remove(col)
                ignore_columns.append(col)

                # Print what happened
                print(f"Unique values for column {col} are over 90% of dataset diversity. Discarding column.")
    
    return ignore_columns, numerical_columns, categorical_columns

def prepare_dataframe_to_ml(df):
    '''
    Prepares a dataframe for machine learning by:
    - Removing columns with high correlation with other columns
    - Downcasting numeric columns to float32
    - Casting categorical columns to string
    - Filling missing values with -1 or 'Undefined'
    - Removing columns that are not numerical or categorical
    - Using prince to handle mix of categorical and numerical columns
    - Returns the prepared dataframe
    '''
    ignore_columns, numerical_columns, categorical_columns = identify_numeric_and_categoric_columns(df)

    high_correlation_features = find_high_correlation_features(df, categorical_columns, ignore_columns)

    # Remove high correlation features from categorical columns
    if len(high_correlation_features) > 0:
        # Drop high correlation features from the dataframe
        df.drop(high_correlation_features, axis=1, inplace=True)

        # Remove high correlation features from the categorical and numerical columns, if they exist
        categorical_columns = [col for col in categorical_columns if col not in high_correlation_features]
        numerical_columns = [col for col in numerical_columns if col not in high_correlation_features]

    # Ignore all columns that are not numerical or categorical
    current_ignore_columns = list(set([c for c in df.columns if c not in numerical_columns + categorical_columns]))
    df = df.drop(current_ignore_columns, axis=1)

    if categorical_columns:
        # Fill missing values with 'Indefinido'
        df[categorical_columns] = df[categorical_columns].fillna('Undefined')

        # Cast all categorical columns to string
        df[categorical_columns] = df[categorical_columns].astype(str)

    if numerical_columns:
        # Fill missing values with -1
        df[numerical_columns] = df[numerical_columns].fillna(-1)

    # Downcast numeric columns to float32 to save memory
    for column in numerical_columns:
        df[column] = pd.to_numeric(df[column], downcast='float')

    # Decide on how to handle mix of categorical and numerical columns using prince
    if len(categorical_columns) > 0 and len(numerical_columns) > 0:
        # Use FAMD
        famd = prince.FAMD(
            n_components=(len(categorical_columns) + len(numerical_columns)) - 1,
            n_iter=3,
            copy=True,
            check_input=True,
            random_state=42,
            engine="sklearn",
            handle_unknown="ignore"
        )
        return famd.fit_transform(df)
    elif len(categorical_columns) > 0:
        # Use MCA
        mca = prince.MCA(
            n_components=len(categorical_columns) - 1,
            n_iter=3,
            copy=True,
            check_input=True,
            engine='sklearn',
            random_state=42
        )
        return mca.fit_transform(df)
    else:
        # Only numerical columns
        return df[numerical_columns]

def recommend_items_factorization(df, num_factors=20, num_iterations=5, reg=0.1):
    """
    Given a pandas DataFrame with columns: source, item, rating,
    this function factorizes the rating matrix using ALS and returns a DataFrame
    with columns: source, recommended_item, recommendation_score.

    "source" could be a customer ID, depending on the context.
    "item" could be a item ID, depending on the context.
    "rating" could be a rating value, depending on the context.
    
    Parameters:
        - df (pd.DataFrame): Input dataframe with 'source', 'item', 'rating'
        - num_factors (int): Number of latent factors for factorization.
            This is the number of latent features (or dimensions) used to
            represent both customers and items. Each customer and item
            is modeled as a vector of this length, capturing underlying characteristics.
            A higher number can capture more subtle relationships but may
            require more data and increase computation.
        - num_iterations (int): Number of ALS iterations.
            This represents the number of times the Alternating Least Squares (ALS)
            algorithm iterates. During each iteration, the algorithm alternates between
            updating user and item factors to better approximate the original rating
            matrix. More iterations can improve accuracy, but after a certain point,
            the gains might be minimal.
        - reg (float): Regularization parameter.
            The reg parameter adds a penalty term during the least squares optimization.
            This helps prevent overfitting by discouraging overly complex models
            (i.e., very large factor values) and ensuring the model generalizes better
            to new data. Adjusting this parameter helps balance the fit and the simplicity
            of the model.
                > Increase reg (higher regularization):
                Model becomes simpler (smaller factor values).
                Reduces overfitting (better generalization to new data).
                May lead to underfitting (model might not capture patterns well).
                
                > Decrease reg (lower regularization):
                Model becomes more flexible (larger factor values).
                Can fit the training data better but risks overfitting.
                Predictions may become less stable on unseen data.
        
    Returns:
        pd.DataFrame: DataFrame with columns: source, recommended_item, recommendation_score.
    """
    # Map unique customer and item IDs to indices
    unique_customers = df['source'].unique()
    unique_items = df['item'].unique()
    customer_to_idx = {customer: idx for idx, customer in enumerate(unique_customers)}
    item_to_idx = {item: idx for idx, item in enumerate(unique_items)}
    
    # Build the sparse rating matrix
    row = df['source'].map(customer_to_idx).values
    col = df['item'].map(item_to_idx).values
    if 'rating' not in df.columns:
        data = np.ones(len(row))
    else:
        data = df['rating'].values
    num_customers = len(unique_customers)
    num_items = len(unique_items)
    rating_matrix = csr_matrix((data, (row, col)), shape=(num_customers, num_items))
    
    # Pre-convert to CSC for item updates (saves repeated conversion)
    rating_matrix_csc = rating_matrix.tocsc()
    
    # Initialize latent factors with random values
    user_factors = np.random.rand(num_customers, num_factors)
    item_factors = np.random.rand(num_items, num_factors)
    I = np.eye(num_factors)
    
    # ALS optimization: alternate between updating user and item factors
    for iteration in range(num_iterations):
        print(f"Iteration {iteration+1}/{num_iterations}")
        # Update user factors
        for u in range(num_customers):
            # Find indices of items rated by user u
            start_ptr = rating_matrix.indptr[u]
            end_ptr = rating_matrix.indptr[u+1]
            indices = rating_matrix.indices[start_ptr:end_ptr]
            if len(indices) == 0:
                continue
            ratings_u = rating_matrix.data[start_ptr:end_ptr]
            # Select latent factors for these items
            Y = item_factors[indices, :]
            # Solve (Y^T Y + reg*I) * x = Y^T * r  for user u's factors
            A = Y.T @ Y + reg * I
            b = Y.T @ ratings_u
            user_factors[u, :] = np.linalg.solve(A, b)
        
        # Update item factors
        for i in range(num_items):
            # Find indices of users who rated item i
            start_ptr = rating_matrix_csc.indptr[i]
            end_ptr = rating_matrix_csc.indptr[i+1]
            indices = rating_matrix_csc.indices[start_ptr:end_ptr]
            if len(indices) == 0:
                continue
            ratings_i = rating_matrix_csc.data[start_ptr:end_ptr]
            # Select latent factors for these users
            X = user_factors[indices, :]
            # Solve (X^T X + reg*I) * x = X^T * r  for item i's factors
            A = X.T @ X + reg * I
            b = X.T @ ratings_i
            item_factors[i, :] = np.linalg.solve(A, b)
    
    # Compute predicted ratings by multiplying the factor matrices
    predicted = user_factors.dot(item_factors.T)
    
    # For each user, select the item with the highest predicted rating.
    # (Optionally, one could mask out items already rated.)
    recommended_idx = np.argmax(predicted, axis=1)
    recommendation_scores = np.max(predicted, axis=1)
    
    # Create a results DataFrame mapping indices back to IDs
    result_df = pd.DataFrame({
        'source': unique_customers,
        'recommended_item': [unique_items[idx] for idx in recommended_idx],
        'recommendation_score': recommendation_scores
    })
    return result_df

def sequence_mining_analysis(df, id_col, date_col, analysis_col):
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        raise TypeError(f"Column '{date_col}' must be datetime.")
    
    df = (df[[id_col, date_col, analysis_col]]
          .sort_values([id_col, date_col]))

    grp = df.groupby(id_col)[analysis_col]
    df = df.assign(prev=grp.shift(), curr=df[analysis_col], nxt=grp.shift(-1))
    df = df.dropna(subset=['curr'])

    raw_antec = pd.crosstab(df['curr'], df['prev'])
    raw_conseq = pd.crosstab(df['prev'], df['curr'])

    raw_antec = raw_antec.loc[:, (raw_antec != 0).any(axis=0)]
    raw_antec = raw_antec[(raw_antec.T != 0).any()]

    raw_conseq = raw_conseq.loc[:, (raw_conseq != 0).any(axis=0)]
    raw_conseq = raw_conseq[(raw_conseq.T != 0).any()]

    antec = raw_antec.div(raw_antec.sum(axis=1), axis=0).mul(100)
    conseq = raw_conseq.div(raw_conseq.sum(axis=1), axis=0).mul(100)

    results = []
    for cat in df[analysis_col].unique():
        if cat in antec.index:
            ant_items = antec.loc[cat].dropna()
            ant_items = ant_items[ant_items > 0].sort_values(ascending=False)
            antecedents = [{k: f"{v:.4f}%"} for k, v in ant_items.items()]
        else:
            antecedents = []

        if cat in conseq.index:
            cons_items = conseq.loc[cat].dropna()
            cons_items = cons_items[cons_items > 0].sort_values(ascending=False)
            consequents = [{k: f"{v:.4f}%"} for k, v in cons_items.items()]
        else:
            consequents = []

        results.append({
            "target": cat,
            "antecedents": antecedents,
            "consequents": consequents,
        })

    return results

def _rules_preprocess(df, discard_id=True, id_column='User_ID', bins=3):
    bin_ranges = {}

    if discard_id and id_column in df.columns:
        df = df.drop(columns=[id_column])

    for col in df.select_dtypes(include='number').columns:
        disc = KBinsDiscretizer(n_bins=bins, encode='ordinal', strategy='quantile')
        binned = disc.fit_transform(df[[col]]).astype(int).flatten()
        edges = disc.bin_edges_[0]
        labels = []
        for b in binned:
            left = round(edges[b], 2)
            right = round(edges[b + 1], 2)
            label = f"{col}_in_[{left}-{right}]"
            labels.append(label)
        df[col] = labels
        bin_ranges[col] = edges

    for col in df.select_dtypes(include='datetime').columns:
        df[col] = pd.to_datetime(df[col])
        df[f"{col}_month"] = df[col].dt.month.astype(str)
        df = df.drop(columns=[col])

    for col in df.columns:
        df[col] = df[col].astype(str)

    return df

def _rule_worker(args):
    df, antecedent, all_items, min_support, min_confidence = args
    n = len(df)
    ant_mask = np.ones(n, dtype=bool)
    for cond in antecedent:
        col, val = cond.split('=')
        ant_mask &= (df[col].values == val)

    ant_support = ant_mask.sum() / n
    if ant_support < min_support:
        return []

    rules = []
    for cons in all_items:
        if cons in antecedent:
            continue
        col, val = cons.split('=')
        cons_mask = (df[col].values == val)
        joint = (ant_mask & cons_mask).sum() / n
        if joint == 0:
            continue
        confidence = joint / ant_support
        if confidence >= min_confidence:
            rules.append({
                'antecedent': antecedent,
                'consequent': cons,
                'support': round(joint, 4),
                'confidence': round(confidence, 4)
            })
    return rules

def _mine_patterns_parallel(df, min_support=0.05, min_confidence=0.6, max_antecedents=2):
    all_items = [f"{col}={val}" for col in df.columns for val in df[col].unique()]
    cond_sets = []
    for size in range(1, max_antecedents + 1):
        cond_sets.extend(combinations(all_items, size))

    args = [(df, list(ant), all_items, min_support, min_confidence) for ant in cond_sets]

    with Pool(processes=cpu_count()) as pool:
        results = pool.map(_rule_worker, args)

    flat_results = [rule for batch in results for rule in batch]
    return pd.DataFrame(flat_results)

def analyze_patterns(file_path, discard_id=True, id_column='User_ID', bins=3, min_support=0.05, min_confidence=0.6):
    df = pd.read_csv(file_path)
    df = _rules_preprocess(df, discard_id, id_column, bins)
    rules = _mine_patterns_parallel(df, min_support, min_confidence)
    rules = rules.rename(columns={
        'support': 'rule_frequency',
        'confidence': 'rule_reliability'
    })
    return rules

def recommendation_engine_co_occurrence(
    df,
    user_col,
    item_col,
    rating_col=None,
    date_col=None,
    top_n=5,
    consider_order=False,
    generate_for_all_users=False,
    per_user_n=5
):
    """
    Build a lightweight item recommendation function based on co-occurrence 
    or sequential transitions of items.

    Parameters:
    ----------
    df : pandas.DataFrame
        Input dataframe containing user-item interactions.
    user_col : str
        Column name representing user/customer ID.
    item_col : str
        Column name representing item ID.
    rating_col : str, optional
        Column name representing the strength of the interaction (e.g., rating, frequency, or recency-weighted score).
        If None, all interactions are weighted equally.
    date_col : str, optional
        Column name representing the timestamp of the interaction. 
        Required if consider_order=True to determine the order of interactions.
    top_n : int, default=5
        Number of top recommended items to return when using the recommender function.
    consider_order : bool, default=False
        - If False: recommend items based on co-occurrence (orderless).
        - If True: recommend items based on sequential transitions (order matters).
    generate_for_all_users : bool, default=False
        - If False: returns a recommender function that takes a item_id and returns top_n recommendations.
        - If True: returns a dictionary with user_id as key and a list of up to per_user_n recommended item_ids as value.
    per_user_n : int, default=5
        Number of recommendations to return per user when generate_for_all_users=True.

    Returns:
    -------
    recommend : function or dict
        - If generate_for_all_users=False: returns a function that takes a item_id and returns top_n recommended item_ids.
        - If generate_for_all_users=True: returns a dict {user_id: [recommended_item_ids]}.

    Example:
    -------
    >>> recommender = item_recommendation(df, 'customer_id', 'item_id')
    >>> recommender('A')
    ['B', 'C', 'D']

    >>> user_recs = item_recommendation(df, 'customer_id', 'item_id', generate_for_all_users=True)
    >>> user_recs[123]
    ['A', 'B', 'C']
    """

    df = df[[user_col, item_col] + ([rating_col] if rating_col else []) + ([date_col] if date_col else [])]
    if date_col:
        df = df.sort_values([user_col, date_col])

    pair_scores = {}

    def process_group(group):
        items = group[item_col].tolist()
        ratings = group[rating_col].tolist() if rating_col else [1.0] * len(items)

        if consider_order:
            for (a, b), r in zip(zip(items, items[1:]), ratings):
                pair_scores[(a, b)] = pair_scores.get((a, b), 0) + r
        else:
            item_set = set(items)
            for a, b in combinations(item_set, 2):
                ra = ratings[items.index(a)]
                rb = ratings[items.index(b)]
                weight = (ra + rb) / 2
                pair_scores[(a, b)] = pair_scores.get((a, b), 0) + weight
                pair_scores[(b, a)] = pair_scores.get((b, a), 0) + weight

    df.groupby(user_col).apply(process_group)

    co_matrix = {}
    for (a, b), score in pair_scores.items():
        co_matrix.setdefault(a, {})
        co_matrix[a][b] = score

    for a in co_matrix:
        total = sum(co_matrix[a].values())
        co_matrix[a] = {k: v / total for k, v in co_matrix[a].items()}

    def recommend(item_id):
        if item_id not in co_matrix:
            return []
        sorted_items = sorted(co_matrix[item_id].items(), key=lambda x: x[1], reverse=True)
        return [item for item, _ in sorted_items[:top_n]]

    if not generate_for_all_users:
        return recommend

    records = []
    user_groups = df.groupby(user_col)
    for user_id, group in user_groups:
        items = set(group[item_col])
        candidates = {}
        for item in items:
            if item not in co_matrix:
                continue
            for candidate, score in co_matrix[item].items():
                if candidate in items:
                    continue
                candidates[candidate] = candidates.get(candidate, 0) + score

        sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        for candidate, score in sorted_candidates[:per_user_n]:
            records.append({
                user_col: user_id,
                'recommended_product': candidate,
                'score': score
            })

    return pd.DataFrame(records)

class TextClassifier:
    def __init__(self):
        self.classifier = None
        self.label_encoder = None

    def get_embeddings_enhanced(self, texts):
        text_embeddings = extract_embeddings(texts, EmbeddingType.SEMANTIC)
        hash_text_features = extract_embeddings(texts, EmbeddingType.TEXTUAL)
        text_embeddings = np.array(text_embeddings) # shape (1496, 512)
        hash_text_features = np.array(hash_text_features) # shape (1496, 512)
        return np.concatenate((text_embeddings, hash_text_features), axis=1)

    def train(self, texts: List[str], labels: List[str], test_size=0.2):
        df = pd.DataFrame({"text": texts, "label": labels})
        df = df.drop_duplicates(subset="text")

        X = df["text"].values
        y = df["label"].values

        X_processed = self.get_embeddings_enhanced(X)

        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)

        # Avoid converting to list and back to numpy arrays
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y_encoded, test_size=test_size, random_state=42 # Added random_state for reproducibility
        )

        self.classifier = MLPClassifier(random_state=1, max_iter=500)
        self.classifier.fit(X_train, y_train)

        test_score = self.classifier.score(X_test, y_test)
        train_score = self.classifier.score(X_train, y_train)
        print(f"Train accuracy: {train_score}")
        print(f"Test accuracy: {test_score}")

        # Retrain on all data
        self.classifier.fit(X_processed, y_encoded)

    def predict(self, text):
        if self.classifier is None or self.label_encoder is None:
            raise RuntimeError("Classifier has not been trained or loaded.")

        features = self.get_embeddings_enhanced([text])
        pred_encoded = self.classifier.predict(features)
        proba = self.classifier.predict_proba(features)

        pred_label = self.label_encoder.inverse_transform(pred_encoded)[0]
        predicted_class_index = self.classifier.classes_.tolist().index(pred_encoded[0])
        predicted_proba_value = proba[0][predicted_class_index]

        return pred_label, float(predicted_proba_value)

    def predict_batch(self, texts):
        if self.classifier is None or self.label_encoder is None:
            raise RuntimeError("Classifier has not been trained or loaded.")

        features = self.get_embeddings_enhanced(texts)
        pred_encoded = self.classifier.predict(features)
        proba = self.classifier.predict_proba(features)

        pred_labels = self.label_encoder.inverse_transform(pred_encoded)

        results = []
        for i in range(len(texts)):
            predicted_class_index = self.classifier.classes_.tolist().index(pred_encoded[i])
            predicted_proba_value = proba[i][predicted_class_index]
            results.append((pred_labels[i], float(predicted_proba_value)))

        return results

    def save(self, filename):
        with open(filename, 'wb') as f:
            cloudpickle.dump(self, f)

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return cloudpickle.load(f)
