from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime

import json

from apscheduler.schedulers.background import BackgroundScheduler
from bson import ObjectId
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    status,
    encoders,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from starlette.background import BackgroundTasks
from starlette.middleware.gzip import GZipMiddleware

# original function
_original_jsonable_encoder = encoders.jsonable_encoder

def correct_return(document):
    """
    Recursively convert ObjectId instances to strings in a document.
    """
    if isinstance(document, dict):
        return {k: correct_return(v) for k, v in document.items()}
    elif isinstance(document, list):
        return [correct_return(item) for item in document]
    elif isinstance(document, ObjectId):
        return str(document)
    else:
        return document

# Create patched version
def patched_jsonable_encoder(*args, **kwargs):
    result = _original_jsonable_encoder(*args, **kwargs)
    try:
        # Patch the specific dict conversion part
        if isinstance(result, dict):
            result = dict(correct_return(result))
    except Exception:
        pass
    return result

# Apply the patch
encoders.jsonable_encoder = patched_jsonable_encoder

@asynccontextmanager
async def default_lifespan(app: FastAPI):
    yield

dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Request Logs Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }
        .filters {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .filter-group {
            margin: 10px 0;
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        input, select, button {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin: 2px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        #logs-table {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
        }
        .log-row:hover {
            background-color: #f5f5f5;
        }
        pre {
            margin: 0;
            white-space: pre-wrap;
            max-width: 300px;
            max-height: 100px;
            overflow: auto;
        }
        canvas {
            max-width: 100%;
            margin: 10px 0;
        }
        .pagination {
            display: flex;
            justify-content: center;
            margin-top: 10px;
        }
        .pagination button {
            margin: 0 5px;
            padding: 5px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            background-color: white;
            color: black;
        }
        .pagination button.active {
            background-color: #007bff;
            color: white;
            border-color: #007bff;
        }
        .pagination button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="filters">
        <div class="filter-group">
            <input type="datetime-local" id="start">
            <input type="datetime-local" id="end">
            <input type="text" id="endpoint" placeholder="Endpoint">
            <select id="method">
                <option value="">All Methods</option>
                <option>GET</option>
                <option>POST</option>
                <option>PUT</option>
                <option>DELETE</option>
            </select>
            <input type="text" id="client_ip" placeholder="Client IP">
            <button onclick="loadLogs()">Filter</button>
        </div>
    </div>

    <div class="charts-grid">
        <div class="chart-container">
            <h3>Requests Timeline</h3>
            <canvas id="timelineChart"></canvas>
        </div>
        <div class="chart-container">
            <h3>Endpoint Distribution</h3>
            <canvas id="endpointChart"></canvas>
        </div>
        <div class="chart-container">
            <h3>HTTP Methods</h3>
            <canvas id="methodChart"></canvas>
        </div>
        <div class="chart-container">
            <h3>Top Client IPs</h3>
            <canvas id="ipChart"></canvas>
        </div>
    </div>

    <div id="logs-table">
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Method</th>
                    <th>Endpoint</th>
                    <th>Client IP</th>
                    <th>Query Params</th>
                    <th>Headers</th>
                    <th>Body</th>
                </tr>
            </thead>
            <tbody id="logs-body">
            </tbody>
        </table>
    </div>

    <div class="pagination" id="pagination-controls">
        <button onclick="changePage(currentPage - 1)" id="prev-page" disabled>Previous</button>
        <span id="current-page-number">1</span>
        <button onclick="changePage(currentPage + 1)" id="next-page">Next</button>
    </div>

    <script>
        let charts = {
            timeline: null,
            endpoint: null,
            method: null,
            ip: null
        };
        let currentPage = 1;
        const pageSize = 25;
        let totalLogs = 0;

        async function fetchMetrics() {
            const response = await fetch('/api/metrics');
            const metrics = await response.json();

            // Process timeline data
            const timelineLabels = Object.keys(metrics.request_counts_per_minute).reverse();
            const timelineData = Object.values(metrics.request_counts_per_minute).reverse();
            if (charts.timeline) charts.timeline.destroy();
            charts.timeline = new Chart(document.getElementById('timelineChart'), {
                type: 'line',
                data: {
                    labels: timelineLabels,
                    datasets: [{
                        label: 'Requests per Minute',
                        data: timelineData,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                }
            });

            // Process endpoint data
            const endpointLabels = Object.keys(metrics.endpoint_counts);
            const endpointData = Object.values(metrics.endpoint_counts);
            if (charts.endpoint) charts.endpoint.destroy();
            charts.endpoint = new Chart(document.getElementById('endpointChart'), {
                type: 'bar',
                data: {
                    labels: endpointLabels,
                    datasets: [{
                        label: 'Requests per Endpoint',
                        data: endpointData,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgb(54, 162, 235)',
                        borderWidth: 1
                    }]
                }
            });

            // Process method data
            const methodLabels = Object.keys(metrics.method_counts);
            const methodData = Object.values(metrics.method_counts);
            if (charts.method) charts.method.destroy();
            charts.method = new Chart(document.getElementById('methodChart'), {
                type: 'pie',
                data: {
                    labels: methodLabels,
                    datasets: [{
                        label: 'HTTP Methods',
                        data: methodData,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(255, 205, 86, 0.2)',
                            'rgba(153, 102, 255, 0.2)'
                        ],
                        borderColor: [
                            'rgb(255, 99, 132)',
                            'rgb(75, 192, 192)',
                            'rgb(255, 205, 86)',
                            'rgb(153, 102, 255)'
                        ],
                        borderWidth: 1
                    }]
                }
            });

            // Process IP data
            const ipLabels = Object.keys(metrics.top_client_ips);
            const ipData = Object.values(metrics.top_client_ips);
            if (charts.ip) charts.ip.destroy();
            charts.ip = new Chart(document.getElementById('ipChart'), {
                type: 'bar',
                data: {
                    labels: ipLabels,
                    datasets: [{
                        label: 'Requests per IP',
                        data: ipData,
                        backgroundColor: 'rgba(255, 159, 64, 0.2)',
                        borderColor: 'rgb(255, 159, 64)',
                        borderWidth: 1
                    }]
                }
            });
        }

        function formatDateTimeLocal(value) {
            if (!value) return null;
            const date = new Date(value);
            date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
            return date.toISOString().slice(0, 19).replace('T', ' ');
        }

        async function loadLogs(newPage = 1) {
            currentPage = newPage;
            const data = {
                start: formatDateTimeLocal(document.getElementById('start').value),
                end: formatDateTimeLocal(document.getElementById('end').value),
                endpoint: document.getElementById('endpoint').value,
                method: document.getElementById('method').value,
                client_ip: document.getElementById('client_ip').value,
                page: currentPage,
                page_size: pageSize
            };

            console.log("Sending Data:", data); // Debugging

            const response = await fetch(`/api/logs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const paginatedLogs = await response.json();
            const logs = paginatedLogs.items;
            totalLogs = paginatedLogs.total;

            // Update table
            const tbody = document.getElementById('logs-body');
            tbody.innerHTML = '';

            logs.forEach(log => {
                const row = document.createElement('tr');
                row.className = 'log-row';
                row.innerHTML = `
                    <td>${new Date(log.timestamp).toLocaleString()}</td>
                    <td>${log.method}</td>
                    <td>${log.endpoint}</td>
                    <td>${log.client_ip}</td>
                    <td><pre>${JSON.stringify(log.query_params, null, 2)}</pre></td>
                    <td><pre>${JSON.stringify(log.headers, null, 2)}</pre></td>
                    <td><pre>${log.body}</pre></td>
                `;
                tbody.appendChild(row);
            });

            // Update pagination controls
            const prevButton = document.getElementById('prev-page');
            const nextButton = document.getElementById('next-page');
            const currentPageSpan = document.getElementById('current-page-number');

            currentPageSpan.textContent = currentPage;
            prevButton.disabled = currentPage === 1;
            nextButton.disabled = currentPage * pageSize >= totalLogs;
        }

        function changePage(newPage) {
            if (newPage > 0 && newPage <= Math.ceil(totalLogs / pageSize)) {
                loadLogs(newPage);
            }
        }

        // Load initial data
        fetchMetrics();
        loadLogs();
    </script>
</body>
</html>
"""

class FastAPIWrapper:
    def __init__(self, lifespan=None, username="admin", password="password"):
        self.scheduler = None
        self.app = FastAPI(
            lifespan=lifespan if lifespan else default_lifespan,
            default_response_class=ORJSONResponse
        )
        self.username = username
        self.password = password
        self.security = HTTPBasic()
        self._setup_db()
        self._setup_scheduler()
        self._setup_middlewares()
        self._setup_routes()

    def _setup_db(self):
        self.SQLALCHEMY_DATABASE_URL = "sqlite:///./request_logs.db"
        self.engine = create_engine(
            self.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()

        class RequestLog(self.Base):
            __tablename__ = "request_logs"
            id = Column(Integer, primary_key=True, index=True)
            client_ip = Column(String)
            endpoint = Column(String)
            method = Column(String)
            headers = Column(String)
            query_params = Column(String)
            body = Column(String)
            timestamp = Column(DateTime)

        self.RequestLog = RequestLog
        self.Base.metadata.create_all(bind=self.engine)

    def _setup_scheduler(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self._scheduled_cleanup, 'interval', minutes=60)
        self.scheduler.start()

    def _scheduled_cleanup(self):
        db = self.SessionLocal()
        try:
            total_logs = db.execute("SELECT COUNT(*) FROM request_logs").scalar()
            if total_logs > 2000000:
                db.execute("""
                    DELETE FROM request_logs 
                    WHERE timestamp <= (
                        SELECT timestamp FROM request_logs 
                        ORDER BY timestamp ASC 
                        LIMIT 1 OFFSET 2000000
                    )
                """)
                db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error during cleanup: {e}")
        finally:
            db.close()

    def _setup_middlewares(self):
        self.app.add_middleware(
            CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
        )
        self.app.add_middleware(GZipMiddleware, minimum_size=500)

        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            body = await request.body()

            async def receive():
                return {"type": "http.request", "body": body, "more_body": False}

            request._receive = receive
            response = await call_next(request)

            async def save_log():
                try:
                    body_str = body.decode("utf-8")
                except UnicodeDecodeError:
                    body_str = str(body)

                db = self.SessionLocal()
                try:
                    log_entry = self.RequestLog(
                        client_ip=request.client.host if request.client else None,
                        endpoint=request.url.path,
                        method=request.method,
                        headers=json.dumps(dict(request.headers)),
                        query_params=json.dumps(dict(request.query_params)),
                        body=body_str,
                        timestamp=datetime.now(),
                    )
                    db.add(log_entry)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    print(f"Error saving log: {e}")
                finally:
                    db.close()

            background = BackgroundTasks()
            background.add_task(save_log)
            response.background = background
            return response

    def _setup_routes(self):
        class PaginatedLogs(BaseModel):
            total: int
            items: List[dict]

        class LogMetrics(BaseModel):
            request_counts_per_minute: dict
            endpoint_counts: dict
            method_counts: dict
            top_client_ips: dict

        class LogListingInput(BaseModel):
            start: Optional[str] = None
            end: Optional[str] = None
            endpoint: Optional[str] = None
            method: Optional[str] = None
            client_ip: Optional[str] = None
            page: int = 1
            page_size: int = 25

        def get_db():
            db = self.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        def parse_string_into_datetime(dt_string):
            return datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")

        def authenticate(credentials: HTTPBasicCredentials = Depends(self.security)):
            correct_username = credentials.username == self.username
            correct_password = credentials.password == self.password
            if not (correct_username and correct_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Basic"},
                )
            return credentials.username

        @self.app.post("/api/logs", response_model=PaginatedLogs)
        async def get_logs(
            data_input: LogListingInput,
            db=Depends(get_db),
            username: str = Depends(authenticate)
        ):
            query = db.query(self.RequestLog)

            if data_input.start:
                query = query.filter(
                    self.RequestLog.timestamp >= parse_string_into_datetime(data_input.start)
                )
            if data_input.end:
                query = query.filter(
                    self.RequestLog.timestamp <= parse_string_into_datetime(data_input.end)
                )
            if data_input.endpoint:
                query = query.filter(self.RequestLog.endpoint.contains(data_input.endpoint))
            if data_input.method:
                query = query.filter(self.RequestLog.method == data_input.method)
            if data_input.client_ip:
                query = query.filter(self.RequestLog.client_ip == data_input.client_ip)

            total = query.count()
            logs = (
                query.order_by(self.RequestLog.timestamp.desc())
                .offset((data_input.page - 1) * data_input.page_size)
                .limit(data_input.page_size)
                .all()
            )

            return PaginatedLogs(
                total=total,
                items=[
                    {
                        "timestamp": log.timestamp.isoformat(),
                        "method": log.method,
                        "endpoint": log.endpoint,
                        "client_ip": log.client_ip,
                        "query_params": json.loads(log.query_params),
                        "headers": json.loads(log.headers),
                        "body": log.body,
                    }
                    for log in logs
                ],
            )

        @self.app.get("/api/metrics", response_model=LogMetrics)
        async def get_metrics(
            db=Depends(get_db),
            username: str = Depends(authenticate)
        ):
            logs = db.query(self.RequestLog).order_by(self.RequestLog.timestamp.desc()).all()

            timeline_data = {}
            endpoint_counts = {}
            method_counts = {}
            ip_counts = {}

            for log in logs:
                date = log.timestamp
                minute = f"{date.year}-{date.month:02}-{date.day:02} {date.hour:02}:{date.minute:02}"
                timeline_data[minute] = timeline_data.get(minute, 0) + 1
                endpoint_counts[log.endpoint] = endpoint_counts.get(log.endpoint, 0) + 1
                method_counts[log.method] = method_counts.get(log.method, 0) + 1
                ip_counts[log.client_ip] = ip_counts.get(log.client_ip, 0) + 1

            top_ips = dict(sorted(ip_counts.items(), key=lambda item: item[1], reverse=True)[:10])

            return LogMetrics(
                request_counts_per_minute=timeline_data,
                endpoint_counts=endpoint_counts,
                method_counts=method_counts,
                top_client_ips=top_ips,
            )

        @self.app.get("/api/dashboard", response_class=HTMLResponse)
        async def dashboard(username: str = Depends(authenticate)):
            return HTMLResponse(content=dashboard_html)

# if __name__ == "__main__":
#     wrapper = FastAPIWrapper()
#     app = wrapper.app
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8005)
