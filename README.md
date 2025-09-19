# Forró Archive

A Telegram media crawler that automatically downloads and organizes forró music files with deduplication, metadata extraction, and Navidrome integration for playback.

## Features

- **Telegram Integration**: Crawls Telegram groups/channels for media files
- **Deduplication**: Prevents duplicate downloads using file hashing
- **Metadata Preservation**: Extracts and stores original filenames and message metadata
- **Web API**: FastAPI-based control panel for monitoring and manual crawling
- **Music Server**: Integrated Navidrome for web-based music playback
- **Docker Support**: Containerized deployment with docker-compose

## Quick Start

1. **Setup environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Telegram API credentials and group details
   ```

2. **Initialize directories**:
   ```bash
   make init
   ```

3. **Start all services**:
   ```bash
   make up
   ```

4. **Access services**:
   - API Control Panel: http://localhost:8000
   - Navidrome Music Server: http://localhost:4533

## Configuration

Create a `.env` file with:

```env
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
GROUP=your_telegram_group_name
CRAWL_EVERY_MINUTES=1440  # Daily crawling
```

## API Endpoints

- `GET /status` - Get crawler status and last message ID
- `POST /crawl` - Trigger manual crawl
- `GET /media` - List recent media files (last 100)
- `GET /duplicates` - View duplicate files detected

## Makefile Commands

- `make up` - Start all services
- `make api` - Run only the API service
- `make crawl` - Run crawler once manually
- `make build` - Build all Docker images
- `make down` - Stop all services
- `make logs` - View API logs
- `make logs-crawler` - View crawler logs

## Architecture

- **Crawler** (`apps/crawler/`): Telegram client for downloading media
- **API** (`apps/api/`): FastAPI web interface and scheduler
- **Database**: SQLite for metadata storage
- **Storage**: Local filesystem with organized directory structure
- **Navidrome**: Music server for web-based playback

## Requirements

- Docker and docker-compose
- Telegram API credentials
- Valid Telegram session (created on first manual run)