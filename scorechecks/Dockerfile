# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
FROM 100.65.4.54:30000/scorechecker:v1

ARG SERVICE
ENV SERVICE=${SERVICE}

ARG TEAM
ENV TEAM=${TEAM}

COPY shared/healthcheck_loop.sh ${SERVICE}/ shared/healthz_webserver.py /home/user/

RUN if [ -f "/home/user/requirements.txt" ]; then \
        pip install -r /home/user/requirements.txt ; \
    fi

CMD /bin/bash -c "/home/user/healthcheck_loop.sh $TEAM & /home/user/healthz_webserver.py"
