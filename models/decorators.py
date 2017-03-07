
def banana(fn):
    def f():
        if auth.user_id is None:
            # Not logged in
            redirect(URL('default', 'login'))
        elif auth.user_email not in ["master@me.com"]:
            redirect(URL('default', 'goaway'))
        else:
            return fn()
    return f