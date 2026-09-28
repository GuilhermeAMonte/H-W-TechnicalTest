FROM owasp/modsecurity-crs:nginx

# Stage 7 FIX: substitui o template do cors.conf por uma versão que também injeta
# o header Content-Security-Policy (defesa em profundidade contra DOM XSS via
# fragmento, que o WAF não consegue inspecionar). COPY no build = como root,
# sem o erro de permissão do mount em runtime. O entrypoint faz envsubst normal.
COPY conf/cors.conf /etc/nginx/templates/includes/cors.conf.template
