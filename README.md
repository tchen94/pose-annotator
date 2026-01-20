<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="frontend/src/assets/logo.png">
    <source media="(prefers-color-scheme: light)" srcset="frontend/src/assets/logo-light.png">
    <img alt="Pose Annotator Logo" src="frontend/src/assets/logo.png" height="150">
  </picture>

  <br>

  <img src="https://badgen.net/badge/python/3.12%2B/blue" alt="Python 3.12+">
  <img src="https://badgen.net/badge/nodejs/22%2B/green" alt="Node.js 22+">
  <img src="https://badgen.net/badge/postgresql/15%2B/cyan" alt="PostgreSQL 15+">
  <img src="https://badgen.net/badge/license/MIT/orange" alt="MIT License">

  <br>

<i>A web-based keypoint annotation tool for human pose estimation</i>

</div>

<hr>

**Pose Annotator** is a lightweight, web-based tool for annotating
**keypoints** on video frames for human pose estimation.

### Key Features

- Upload a video and randomly sample a number of frames
- Step through sampled frames
- Annotate up to **17 COCO-format keypoints** via point-and-click
- Export frame annotations to a **CSV** file

<img src="ui-demo.gif" alt="Pose Annotator Demo" style="max-width: 100%; height: auto;" />

<hr>

## Quick Start

### 1) Install Python 3.12+

If you don't have Python installed, download it from the official Python
website: https://www.python.org/downloads.

Verify your installed Python version from the command line:

**macOS / Linux**

```bash
python3 --version
```

**Windows**

```bat
py --version
```

### 2) Install PostgreSQL

1. Download the latest version of PostgreSQL from: https://www.postgresql.org/download/
2. Follow the installation instructions for your operating system.
3. During installation, create a password for the default `postgres` user.
4. After installation, ensure that the PostgreSQL server is running.
5. Install pgAdmin (usually included in the PostgreSQL installer) to manage your databases.
6. Open pgAdmin and connect to your PostgreSQL server using the `postgres` user
   and the password you created during installation.
7. Create a new database named `pose_annotator`.
8. Make sure the database server is running before starting Pose Annotator, using pSQL in pgAdmin:
   ```bash
    \dt # Lists all databases in the current database
   ```
   You can check the status with:
   ```bash
    \conninfo # Displays information about current connections
    SHOW port; # Displays the port number PostgreSQL is listening on
   ```

### 3) Start Pose Annotator Locally

1. Fork and clone this repository
2. Navigate to the `backend` directory and create a virtual environment:

   **macOS / Linux**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   **Windows**

   ```bat
   py -m venv venv
   venv\Scripts\activate
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

**Make sure the PostgreSQL server is running and the `pose_annotator` database is created. Or else the backend server will not start properly.**

4. Create a `.env` file in the `backend` directory and create a `DATABASE_URL` variable with your PostgreSQL connection details:

   ```env
   DATABASE_URL=postgresql://<username>:<password>@localhost:5432/pose_annotator
   ```

   Replace `<username>` and `<password>` with your PostgreSQL credentials.

5. Start the backend server:

   ```bash
    python api.py
   ```

   You should see the following output in the terminal:

   ```bash
   Database initialized successfully.
    * Serving Flask app 'pose-annotator-backend'
    * Debug mode: on
   WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
    * Running on http://127.0.0.1:8000
   Press CTRL+C to quit
   ```

<b>Please make sure you have Node 22+ installed before proceeding. Find the latest download here: https://nodejs.org/en/download.</b>

6. Open a new terminal window, navigate to the `frontend` directory, and install
   the required Node.js packages:

   ```bash
    npm install
   ```

7. Start the frontend development server:

   ```bash
   npm run dev
   ```

   You should see the following output in the terminal:

   ```bash
    VITE <whatever-version-you-have>  ready in <some-time> ms

    ➜  Local:   http://localhost:5173/
    ➜  Network: use --host to expose
   ```

Open your web browser and navigate to `http://localhost:5173/` to access Pose Annotator.
