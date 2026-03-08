# LAMPrEY

LAMPrEY is a Docker-based quality control pipeline server for quantitative proteomics. It is designed for laboratories that want to organize proteomics pipelines, process RAW files automatically, and review QC results through a web interface.

![](docs/img/ProteomicsQC1.png "LAMPrEY interface overview")

Full documentation: [LAMPrEY documentation](https://LewisResearchGroup.github.io/ProteomicsQC/)

## What It Provides

- project and pipeline management through the Django admin
- automated RAW file processing with [MaxQuant](https://maxquant.org/) and [RawTools](https://github.com/kevinkovalchik/RawTools)
- upload queue and per-run job management from the pipeline page
- an interactive QC dashboard with project, pipeline, and uploader filters
- an authenticated API for programmatic access

## Requirements

- Docker Engine
- Docker Compose, either `docker-compose` or `docker compose`
- `make`
- `git-lfs`

## Quick Start

Install Docker Engine and Docker Compose by following the Docker documentation for your platform. For Ubuntu, see [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

The repository stores the bundled MaxQuant executable ZIP with Git LFS. Install `git-lfs` before cloning so `app/seed/defaults/maxquant/MaxQuant_v_2.4.12.0.zip` is downloaded as a real file instead of a small pointer.

If `git lfs` is not available on Ubuntu or Debian, install it first:

```bash
sudo apt update
sudo apt install -y git-lfs
```

Initialize Git LFS before cloning:

```bash
git lfs install
```

Clone the repository:

```bash
git clone git@github.com:LewisResearchGroup/ProteomicsQC.git LAMPrEY
cd LAMPrEY
git lfs pull
```

If you already cloned and only need to materialize the bundled MaxQuant ZIP:

```bash
git lfs pull --include="app/seed/defaults/maxquant/MaxQuant_v_2.4.12.0.zip" --exclude=""
```

If you download the repository from the GitHub web UI instead of cloning it, make sure the repository is configured to include Git LFS objects in archives. Otherwise the archive will contain only the LFS pointer file.

Generate the local configuration:

```bash
./scripts/generate_config.sh
```

This guide uses `make` targets such as `make init` and `make devel` as shortcuts for Docker Compose commands. If your Docker setup requires elevated privileges, run the `make` targets with a user that can use `sudo`; otherwise they run without it.

`make` is a host-side convenience tool. It is not part of Docker and it is not provided by the application container.

On Ubuntu or Debian, install it with:

```bash
sudo apt update
sudo apt install make
```

If `make` is not available on your system, you can still run the equivalent `docker compose ...` commands manually.

Run the first-time setup:

```bash
make init
```

By default, `make init` uses the published container image.

If the published image is unavailable, use the local-build fallback:

```bash
make init-local
```

Start the application:

```bash
make devel   # development server on http://127.0.0.1:8000
make serve   # production-style server on http://localhost:8080
```

## Setup Modes

`make init` performs the first-time setup using the published container image:

- runs migrations
- prompts for a Django superuser
- collects static files
- bootstraps demo data

`make init-local` performs the same setup, but builds the image locally with `docker-compose-develop.yml`.

## Common Commands

```bash
make devel         # start the development stack
make devel-build   # rebuild and start the development stack
make serve         # start the production-style stack
make down          # stop containers
make test          # run tests
```

## Notes

- Generated configuration is stored in `.env`.
- Local persistent data is stored under `./data/`.
- The admin panel is available at `/admin` after startup.
- The dashboard is available at `/dashboard` after login.
- Pipeline uploads and API requests are scoped to the authenticated user's projects.
- The bundled MaxQuant ZIP is stored with Git LFS.
- For installation details, admin usage, API documentation, and operational notes, see the documentation site.
