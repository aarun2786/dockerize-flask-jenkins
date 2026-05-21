# AWS DevSecOps Project — Dockerized Flask Application with Jenkins CI Pipeline & EBS Storage Optimization

## Project Overview

This project demonstrates a complete DevSecOps-style CI/CD environment using:

- Jenkins
- Docker
- Flask Application
- GitHub Webhooks
- AWS EC2
- AWS EBS Storage Optimization

The project focuses not only on application deployment automation but also on real-world infrastructure troubleshooting involving Jenkins storage bottlenecks on AWS.

---

# Architecture

```text
Developer
    │
    ▼
GitHub Repository
    │
    ▼
GitHub Webhook
    │
    ▼
Jenkins Pipeline
    │
    ▼
Docker Build
    │
    ▼
Docker Container
    │
    ▼
Flask Application
```

---

# Extended Infrastructure Architecture

```text
                AWS Cloud
                    │
        ┌──────────────────────┐
        │      EC2 Instance     │
        │    Ubuntu + Jenkins   │
        └──────────────────────┘
                    │
         Root Volume (/dev/root)
                    │
          Low Disk Space Alert
                    │
                    ▼
        ┌──────────────────────┐
        │    Additional EBS     │
        │      3 GB Volume      │
        └──────────────────────┘
                    │
                    ▼
               Mounted to /tmp
                    │
                    ▼
           Jenkins Back Online
```

---

# Technologies Used

| Technology | Purpose |
|---|---|
| AWS EC2 | Jenkins Hosting |
| AWS EBS | Additional Storage |
| Jenkins | CI/CD Automation |
| Docker | Containerization |
| Flask | Python Web Application |
| GitHub | Source Code Management |
| Linux | Server Administration |
| GitHub Webhooks | Pipeline Triggering |

---

# Project Structure

```text
dockerize-flask-jenkins/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── Jenkinsfile
└── README.md
```

---

# Flask Application

## app.py

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Docker Flask App Running"

@app.route('/profile')
def profile():
    return "Profile Page"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
```

---

# Requirements File

## requirements.txt

```text
Flask==3.0.0
```

---

# Dockerfile

```dockerfile
FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

---

# Jenkins Pipeline

## Jenkinsfile

```groovy
pipeline {
    agent any

    stages {

        stage('build docker image') {
            steps {
                sh 'docker build -t flask-app .'
            }
        }

        stage('run docker container') {
            steps {
                sh '''
                docker rm -f flask-container || true

                docker run -d -p 5000:5000 \
                --name flask-container flask-app
                '''
            }
        }
    }
}
```

---

# Jenkins & Docker Setup

## Install Java

```bash
sudo apt update

sudo apt install openjdk-17-jdk -y
```

---

# Install Jenkins

```bash
sudo apt install jenkins -y
```

Start Jenkins:

```bash
sudo systemctl enable jenkins

sudo systemctl start jenkins
```

---

# Install Docker

```bash
sudo apt install docker.io -y
```

Start Docker:

```bash
sudo systemctl enable docker

sudo systemctl start docker
```

---

# Configure Docker Permissions

```bash
sudo usermod -aG docker jenkins
```

Restart services:

```bash
sudo systemctl restart docker

sudo systemctl restart jenkins
```

---

# GitHub Webhook Configuration

Webhook URL:

```text
http://<jenkins-public-ip>:8080/github-webhook/
```

Content Type:

```text
application/json
```

Events:

```text
Just the push event
```

---

# CI/CD Workflow

```text
Git Push
   ↓
GitHub Webhook Trigger
   ↓
Jenkins Pipeline Starts
   ↓
Docker Image Build
   ↓
Old Container Removed
   ↓
New Container Started
   ↓
Flask Application Updated
```

---

# AWS DevSecOps Lab — Resolving Jenkins Storage Bottlenecks using EBS

## Problem Statement

During deployment of Jenkins on an AWS EC2 `t3.small` instance with an 8 GB root volume, Jenkins failed to start and generated critical low disk space alerts.

---

# Root Cause Analysis

## Jenkins Safety Threshold

Jenkins internally monitors available storage.

If free space drops below:

```text
1.0 GiB
```

Jenkins automatically:

- Marks node offline
- Stops daemon startup
- Prevents build database corruption

---

# Root Filesystem Limitation

After:

- Ubuntu installation
- Java installation
- Jenkins setup
- Docker installation
- Package dependencies

Available storage reduced to:

```text
~900 MB
```

This triggered Jenkins safety protection.

---

# Engineered Solution

To avoid modifying the existing root filesystem, a dedicated AWS EBS volume was provisioned and attached dynamically.

---

# Step 1 — Provision Additional EBS Volume

Created:

| Setting | Value |
|---|---|
| Volume Type | gp3 |
| Size | 3 GB |
| AZ | Same as EC2 |

Attached volume appeared as:

```text
/dev/nvme1n1
```

---

# Step 2 — Format EBS Volume

```bash
sudo su -

mkfs -t ext4 /dev/nvme1n1
```

---

# Step 3 — Stop Jenkins Service

```bash
systemctl stop jenkins
```

---

# Step 4 — Mount Additional Storage

```bash
mount /dev/nvme1n1 /tmp
```

---

# Step 5 — Verify Mount Structure

```bash
lsblk
```

---

# Step 6 — Restart Jenkins

```bash
systemctl daemon-reload

systemctl start jenkins
```

---

# Storage Verification

## Check Disk Usage

```bash
df -h
```

Output:

```text
Filesystem       Size  Used Avail Use% Mounted on
/dev/nvme1n1     2.9G  192M  2.6G   7% /tmp
```

---

# Jenkins Health Verification

Jenkins Built-In Node returned:

✅ Online

Metrics:

| Metric | Value |
|---|---|
| Free Disk Space | 3.14 GiB |
| Free Temp Space | 2.53 GiB |
| Response Time | 0ms |

---

# Problems Faced & Solutions

---

## 1. Jenkins Branch Mismatch (`master` vs `main`)

### Problem

```text
ERROR: Couldn't find any revision to build
```

### Root Cause

Jenkins attempted:

```text
origin/master
```

But repository used:

```text
main
```

### Solution

Changed Jenkins branch:

```text
*/master → */main
```

---

## 2. Duplicate Git Checkout

### Problem

Pipeline failed during clone stage.

### Root Cause

Declarative pipeline already performs:

```text
Checkout SCM
```

Manual git stage caused conflict.

### Solution

Removed duplicate clone stage.

---

## 3. Docker Container Exited Immediately

### Debug Command

```bash
docker logs flask-container
```

### Root Cause

Python syntax error inside Flask application.

---

## 4. Flask Route Syntax Error

### Incorrect Code

```python
def profile('/profile')
```

### Corrected Code

```python
@app.route('/profile')
def profile():
```

---

## 5. Jenkins Docker Permission Issue

### Problem

Jenkins could not execute Docker commands.

### Solution

```bash
sudo usermod -aG docker jenkins
```

Restarted Jenkins service.

---

## 6. Jenkins Storage Bottleneck

### Problem

Low disk space prevented Jenkins startup.

### Solution

Provisioned and mounted dedicated EBS storage.

---

## 7. Git Rebase Conflict

### Problem

```text
CONFLICT (add/add): Merge conflict in README.md
```

### Solution

Resolved manually:

```bash
git add .

git rebase --continue
```

---

# Security Group Configuration

| Type | Port | Source |
|---|---|---|
| SSH | 22 | Your IP |
| Jenkins | 8080 | 0.0.0.0/0 |
| Flask App | 5000 | 0.0.0.0/0 |

---

# Important Commands Used

| Purpose | Command |
|---|---|
| Build image | `docker build -t flask-app .` |
| Run container | `docker run -d -p 5000:5000 flask-app` |
| View logs | `docker logs flask-container` |
| Restart Jenkins | `systemctl restart jenkins` |
| Check storage | `df -h` |
| View block devices | `lsblk` |
| Git rebase | `git pull --rebase origin main` |

---

# Skills Learned

| Area | Concepts |
|---|---|
| AWS | EC2 & EBS |
| Jenkins | CI/CD Pipelines |
| Docker | Containerization |
| Linux | System Administration |
| GitHub | Source Control |
| DevOps | Deployment Automation |
| Troubleshooting | Infrastructure Debugging |
| Storage Management | EBS Volume Mounting |

---

# Key DevOps Learnings

- CI/CD automation using Jenkins
- Real-world Docker debugging
- GitHub webhook integration
- Linux storage troubleshooting
- Jenkins disk monitoring behavior
- EBS volume provisioning & mounting
- Git rebase conflict resolution
- Infrastructure reliability practices

---

# Real DevSecOps Takeaways

## Proactive Monitoring

Always validate application-specific safety limits before infrastructure deployment.

---

## Decoupled Storage Architecture

Separating:

- OS filesystem
- Application temporary storage
- Jenkins workspace data

improves stability and resilience.

---

## Infrastructure Troubleshooting

Understanding:

- Linux block devices
- Filesystem mounting
- Jenkins health monitoring
- Docker logs

is critical in production environments.

---


# Future Improvements

- Docker Hub integration
- Multi-stage Jenkins pipeline
- Nginx reverse proxy
- Kubernetes deployment
- Terraform infrastructure automation
- Monitoring with Prometheus & Grafana
- Blue-Green deployment strategy

---

# Final Result

✅ Jenkins CI/CD pipeline configured successfully  
✅ Flask application containerized successfully  
✅ GitHub webhook automation implemented  
✅ Docker container deployed automatically  
✅ Jenkins storage bottleneck resolved using EBS  
✅ Infrastructure stabilized successfully  
✅ Real-world DevSecOps troubleshooting completed
