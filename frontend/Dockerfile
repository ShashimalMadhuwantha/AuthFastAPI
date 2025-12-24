# Multi-stage build for Frontend
# Stage 1: Prepare and optimize static files
FROM alpine:3.19 as builder

WORKDIR /build

# Install tools for minification (optional, for future optimization)
RUN apk add --no-cache \
    findutils

# Copy all frontend files
COPY *.html ./
COPY *.js ./
COPY css/ ./css/
COPY js/ ./js/

# Remove any unnecessary files
RUN find . -name "*.map" -type f -delete && \
    find . -name ".DS_Store" -type f -delete && \
    find . -name "Thumbs.db" -type f -delete

# Stage 2: Minimal nginx runtime
FROM nginx:1.25-alpine

# Remove default nginx files
RUN rm -rf /usr/share/nginx/html/* && \
    rm /etc/nginx/conf.d/default.conf

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/

# Copy optimized files from builder
COPY --from=builder /build /usr/share/nginx/html/

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Switch to non-root user
USER nginx

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
