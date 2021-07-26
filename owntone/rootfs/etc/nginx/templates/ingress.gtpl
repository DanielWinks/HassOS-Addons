server {
    listen {{ .interface }}:8099 default_server;

    include /etc/nginx/includes/server_params.conf;
    include /etc/nginx/includes/proxy_params.conf;


    location / {
        allow   172.30.32.2;
        deny    all;

        proxy_pass http://backend;
        sub_filter_types '*';
        sub_filter 'href="/"'  		'href="index.html"'   r;
        sub_filter 'href="?/(.+?)"?(\s|>)'	'href="$1"$2' 	      r;
        sub_filter 'src="?/(.+?)"?(\s|>)'	'src="$1"$2'          r;
        sub_filter '/(api|admin)/'		'$1/'	              r;
        sub_filter '/admin.html'		'admin.html';
        sub_filter '\/artwork'			'artwork';
    }

}
