def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('postfile', '/post/file')
    config.add_route('getlogopixel','/pixel/getfoto')
    config.add_route('home', '/')

