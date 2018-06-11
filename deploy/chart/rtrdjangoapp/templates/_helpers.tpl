{{- define "name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "fullname" -}}
{{- printf "%s-%s" .Release.Name (include "name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
