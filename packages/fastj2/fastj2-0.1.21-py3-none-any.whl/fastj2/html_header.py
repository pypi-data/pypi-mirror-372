header = """
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ fastj2_app_name }}</title>

  {% if fastj2_css %}
  <style>
    {% include "app.css" %}
  </style>
  {% endif %}

  <script src="https://unpkg.com/htmx.org@1.9.10"></script>

  {% if fastj2_js %}
  <script>
    {% include "app.js" %}
  </script>
  {% endif %}
</head>       
"""