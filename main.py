import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BlogMain(Handler):
    def render_blog(self, blog_id="", title="", body="", error=""):
        top5_blog_posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5 ")

        #self.render("blog.html", blog_id=ID, title=title, body=body, error=error, top5_blog_posts=top5_blog_posts)
        self.render("blog.html", top5_blog_posts=top5_blog_posts)

    def get(self):
        self.render_blog()


class NewPost(Handler):
    def render_new_post(self, title="", body="", error=""):
        self.render("NewPost.html", title=title, body=body, error=error)

    def get(self):
        self.render_new_post()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Blog(title = title, body = body)
            #a.put()
            entry_key = a.put()
            entry_id = entry_key.id()

            self.redirect("/blog/" + str(entry_id))
        else:
            error = "Please provide both a Title and Body for your Blog Post."
            self.render_new_post(title, body, error)


class ViewPostHandler(Handler):
    def render_entry(self, id, title="", body="", error=""):
        blog_entry = Blog.get_by_id(int(id))
        self.render("ViewPost.html", title=blog_entry.title, body=blog_entry.body, error=error, blog_entry=blog_entry)

    def get(self, id):
        if Blog.get_by_id(int(id)):
            self.render_entry(id)
        else:
            error = "No Post can be found for that id."
            self.response.write(error)


app = webapp2.WSGIApplication([
    ('/blog', BlogMain),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)], debug=True)
