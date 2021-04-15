FROM python:3.9-slim
# slim=debian-based. Not using alpine because it has poor python3 support.

# Set pip to have cleaner logs and no saved cache
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=false \
    PIPENV_HIDE_EMOJIS=1 \
    PIPENV_IGNORE_VIRTUALENVS=1 \
    PIPENV_NOSPIN=1

# Install ffmpeg
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends ffmpeg

# Install pipenv
RUN pip install -U pipenv

WORKDIR /PyBoss

# Install project dependencies
COPY Pipfile* ./
RUN pipenv install --deploy --system

# Clean unused packages
RUN rm -rf /var/lib/apt/lists/* && apt-get autoremove --purge -y -qq

# Copy the source code in last to optimize rebuilding the image
COPY . .

# Run the bot
ENTRYPOINT ["python"]
CMD ["-m", "pyboss"]