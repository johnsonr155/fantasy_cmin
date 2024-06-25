-include .env
export

# Virtual environments
# N.B. have to create your .env file first and add the GEMFURY_URL
reqs:
ifeq ($(GEMFURY_URL), )
	@echo "\033[0;31m--- You have not created your .env file. Rename .env.example to .env and replace the GEMFURY_URL placeholder ---"
else
	@echo "GEMFURY_URL = $(GEMFURY_URL)"
	. .venv/bin/activate 
	pip install -r requirements.txt 
	@echo "========================"
	@echo "Virtual environment successfully created. To activate the venv:" 
	@echo "	\033[0;32msource .venv/bin/activate"
endif

## Using venv
venv:
	pyenv exec python -m venv .venv
	make reqs

# Copying your files to s3
copy-to-clean:
	aws s3 cp $(folder) s3://ten-ds-clean-data/$(DATA_PATH)/$(VERSION)/ --recursive

copy-to-raw:
	aws s3 cp $(folder) s3://ten-ds-raw-data/$(DATA_PATH)/$(VERSION)/ --recursive

copy-file-to-raw:
	aws s3 cp $(file) s3://ten-ds-raw-data/$(DATA_PATH)/$(VERSION)/$(file)


# Release commands to deploy your app to AWS
release:
	chmod +x ./scripts/release.sh && ./scripts/release.sh $(instance) $(env)

release-pipeline:
	chmod +x ./scripts/release.sh && ./scripts/release.sh pipeline default

release-dash:
	chmod +x ./scripts/release.sh && ./scripts/release.sh dash $(env)

# Presentations
presentations:
	chmod +x ./scripts/generate-presentations.sh && ./scripts/generate-presentations.sh

list-notebooks:
	@chmod +x ./scripts/generate-presentations.sh && ./scripts/generate-presentations.sh list_notebooks

# Pipeline commands
PIPELINE_PATH=pipeline/$(v)

pipe/run:
	. $(PIPELINE_PATH)/.venv/bin/activate && \
	python $(PIPELINE_PATH)/lambda.py && \
	deactivate

pipe/reqs:
	. $(PIPELINE_PATH)/.venv/bin/activate && \
	pip install -r $(PIPELINE_PATH)/requirements.txt && \
	deactivate

pipe/venv:
	python3 -m venv $(PIPELINE_PATH)/.venv && \
	make pipe/reqs


# Pipeline vs dash build logic

# Docker
ECR_URL=$(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
ECR_REPO_URL=$(ECR_URL)/$(ECR_REPO_NAME)
IMAGE=$(ECR_REPO_URL):$(IMAGE_TAG)

ifdef v
# Build the pipeline if a version is supplied
DOCKER_BUILD_ARGS = --build-arg VERSION=$(v) ./pipeline
ECR_REPO_NAME=$(APP_NAME)-pipeline
IMAGE_TAG=$(v)-$$(sha1sum ./pipeline/$(v)/* | sha1sum | awk '{print $$1;}')
else
# Build the dash if a version is not supplied
DOCKER_BUILD_ARGS = .
ECR_REPO_NAME=$(APP_NAME)-dash
IMAGE_TAG=$$(git rev-parse HEAD)
endif


docker/login:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_URL)

docker/build:
	docker build --build-arg GEMFURY_URL=$(GEMFURY_URL) -t $(ECR_REPO_URL):$(IMAGE_TAG) $(DOCKER_BUILD_ARGS) 

docker/push:
	docker push $(IMAGE)

docker/update-tag:
	MANIFEST=$$(aws ecr batch-get-image --repository-name $(ECR_REPO_NAME) --image-ids imageTag=$(IMAGE_TAG) --query 'images[].imageManifest' --output text) && \
	aws ecr put-image --repository-name $(ECR_REPO_NAME) --image-tag $(tag) --image-manifest "$$MANIFEST"

# Ouputs the value that you're after - useful to get a value i.e. IMAGE_TAG out of the Makefile
docker/echo:
	echo $($(value))

# Terraform
# Set terraform workspace ENV to default if env not specified
ifndef env
override env = default
endif

# Pass image_tag if the instance is dash
ifeq ($(instance), dash)
tf_build_args=-var "image_tag=$(IMAGE_TAG)"
else
tf_build_args=-var "source_hash=$$(sha1sum ./$(instance)/* | sha1sum | awk '{print $$1;}')"
endif

tf/set-workspace:
	terraform -chdir=terraform/$(instance) workspace select $(env)

tf/new-workspace:
	terraform -chdir=terraform/$(instance) workspace new $(env)

# Will create a new workspace if one does not already exist
tf/set-or-create-workspace:
	make tf/set-workspace || make tf/new-workspace

tf/init:
	terraform -chdir=./terraform/$(instance) init

tf/fmt:
	terraform -chdir=./terraform/$(instance) fmt -check -diff

tf/plan:
	make tf/set-workspace && \
	terraform -chdir=./terraform/$(instance) plan ${tf_build_args}

tf/apply:
	make tf/set-workspace && \
	terraform -chdir=./terraform/$(instance) apply -auto-approve ${tf_build_args}

tf/destroy:
	make tf/set-workspace && \
	terraform -chdir=./terraform/$(instance) destroy ${tf_build_args}
