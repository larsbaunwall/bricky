FROM deepset/haystack:base-cpu-v1.13.0 as base

FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv run pip install --upgrade setuptools
RUN pipenv install --system --deploy

FROM base AS runtime

# Copy virtual env from python-deps stage
#COPY --from=python-deps /.venv /.venv
#ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

ENV TIKA_LOG_PATH=/home/appuser

# Install application into container
COPY . .

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]