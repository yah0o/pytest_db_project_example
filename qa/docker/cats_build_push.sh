#! /bin/sh

sh ../../qa/docker/docker_build_push.sh \
--image "cats/app" \
--docker-file ../../ci/images/app/Dockerfile \
--context-dir ../.. \
--user job-platformrc \
--tag cats-local-build \
-b -p
$@