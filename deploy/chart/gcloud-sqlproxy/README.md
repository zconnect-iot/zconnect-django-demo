This was copied from
https://github.com/kubernetes/charts/tree/master/stable/gcloud-sqlproxy

There is a bug in the chart and the repo has 270 open pull requests, so I'm just
copying it here and fixing it.

# Note

This does trim the end of the name of the instance name - don't create
one thing called `this-has-a-long-name-for-some-reason-1` and
`this-has-a-long-name-for-some-reason-2` or it will break
