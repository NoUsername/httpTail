# httpTail

Tail HTTP text resources that support the range header.

Primary use case: streaming (tailing) large logfiles via http

## Examples

```
httpTail "http://localhost:8080/logfile"

httpTail "http://some.remote.server.com/manage/logfile" --cookie="SESSION=grab-session-cookie-from-admin-session"
```

## Missing feature

* Other auth except "stolen cookie" primarily basic auth
* ...

## More info

This was initially created to be able to easily observe logfiles from spring boot applications exposed via the actuator logging endpoint (for more information see https://docs.spring.io/spring-boot/docs/current/reference/html/production-ready-endpoints.html#production-ready-endpoints ).

(c) 2016 Paul Klingelhuber

