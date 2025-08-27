# nginx_statsd_sidecar

The purpose of this container is to be deployed alongside a Docker container
running `nginx` and to report the stats that are reported from the
[ngx_http_stub_status_module](http://nginx.org/en/docs/http/ngx_http_stub_status_module.html)
module to a `statsd` server.  It polls stats from `nginx` every 10 seconds (this is
configurable via an environment variable).

`nginx_statsd_sidecar` reports these stats to statsd:

* `requests` the number of requests that nginx has handled since the last time
  `nginx_statsd_sidecar` retrieved stats from nginx
* `active_connections` the number of currently active nginx connections
* `reading` the number of active nginx connections in reading state
* `writing` the number of active nginx connections in writing state
* `waiting` the number of active nginx connections in waiting state

## Documentation

Please see <nginx_statsd_sidecar.readthedocs.io> for the full set of docs.
