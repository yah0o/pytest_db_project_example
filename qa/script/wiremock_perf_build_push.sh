#! /bin/sh

sh ./docker_build_push.sh \
--image "cats-wiremock-perf/app" \
--docker-file ./wiremock_perf/ci/images/app/Dockerfile \
--context-dir ../.. \
$@