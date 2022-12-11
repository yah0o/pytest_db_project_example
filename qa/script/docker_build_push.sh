#! /bin/sh

help_text() {
  cat <<EOF
    Usage: $0 [ -i|--image DOCKER_IMAGE_NAME ] [ -t|--tag DOCKER_TAG ] [ -f|--docker-file DOCKER_FILE ] [ -c|--context-dir BUILD_CONTEXT_DIR ] [ -u|--user DOCKER_USER ] [-b|--build]  [-p|--publish] [-h|--help]

        DOCKER_IMAGE_NAME           (required) Docker image name.
        DOCKER_TAG                  (optional) Tag to build image with.
        DOCKER_FILE                 (optional) Dockerfile to build.
        DOCKER_BUILD_CONTEXT_DIR    (optional) Context directory to build docker image.
        DOCKER_USER                 (optional) User to login to docker repository.
EOF
  exit 1
}

BUILD=0
PUBLISH=0

while [ $# -gt 0 ]; do
  arg=$1
  case $arg in
  -h | --help)
    help_text
    ;;
  -i | --image)
    DOCKER_IMAGE_NAME="$2"
    shift
    shift
    ;;
  -t | --tag)
    DOCKER_TAG="$2"
    shift
    shift
    ;;
  -f | --docker-file)
    DOCKER_FILE="$2"
    shift
    shift
    ;;
  -c | --context-dir)
    DOCKER_BUILD_CONTEXT_DIR="$2"
    shift
    shift
    ;;
  -u | --user)
    DOCKER_USER="$2"
    shift
    shift
    ;;
  -b | --build)
    BUILD=1
    shift
    ;;
  -p | --publish)
    PUBLISH=1
    shift
    ;;
  *)
    echo "ERROR: Unrecognised option: ${arg}"
    help_text
    exit 1
    ;;
  esac
done

if [ -z "${DOCKER_IMAGE_NAME}" ]; then
  echo "    Docker image name was not provided. Provide: [ -i|--image DOCKER_IMAGE_NAME ]"
  help_text
  exit 1
fi

if [[ ${BUILD} -eq 0 && ${PUBLISH} -eq 0 ]]; then
  echo "    Nothing to do. Provide --build or -publish option."
  help_text
  exit 1
fi

if [ -z "${DOCKER_TAG}" ]; then
  echo "Tag was not provided. Using 'latest'."
fi

DOCKER_TAG=${DOCKER_TAG:=latest}
DOCKER_IMAGE_TAG="${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
DOCKER_IMAGE_LATEST="${DOCKER_IMAGE_NAME}:latest"

if [ ${BUILD} -gt 0 ]; then
  echo "Build image: ${DOCKER_IMAGE_TAG}..."
  docker build -t ${DOCKER_IMAGE_TAG} -f ${DOCKER_FILE} ${DOCKER_BUILD_CONTEXT_DIR}
fi

if [ ${PUBLISH} -gt 0 ]; then
  DOCKER_USER=${DOCKER_USER:=r_sichenko}
  DOCKER_REPO=artifactory.wgdp.io
  DOCKER_REPO_PATH=${DOCKER_REPO}/wtp-docker
  ARTIFACTORY_IMAGE_TAG=${DOCKER_REPO_PATH}/${DOCKER_IMAGE_TAG}
  ARTIFACTORY_IMAGE_LATEST=${DOCKER_REPO_PATH}/${DOCKER_IMAGE_LATEST}

  echo "Login to docker repository: ${DOCKER_REPO}..."
  if [ -z "$DOCKER_PWD" ]; then
    docker login -u ${DOCKER_USER} ${DOCKER_REPO}
  else
    echo "Using env variable DOCKER_PWD..."
    docker login -u ${DOCKER_USER} ${DOCKER_REPO} -p ${DOCKER_PWD}
  fi

  echo "Tag docker image: ${ARTIFACTORY_IMAGE_TAG}..."
  docker tag ${DOCKER_IMAGE_TAG} ${ARTIFACTORY_IMAGE_TAG}
  docker push ${ARTIFACTORY_IMAGE_TAG}

  if [ "${DOCKER_TAG}" != "latest" ]; then
    echo "Tag docker image: ${ARTIFACTORY_IMAGE_LATEST}..."
    docker tag ${DOCKER_IMAGE_TAG} ${ARTIFACTORY_IMAGE_LATEST}
    docker push ${ARTIFACTORY_IMAGE_LATEST}
  fi
fi

echo 'done!'