# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""
    yawpl.py
    
    WordPress xml-rpc client library
    use MovableType API & WordPress API Extensions

    Copyright (C) 2009 Theodore Campbell
    theodore.campbell@stupidfoot.com
    http://stupidfoot.com
    
    Copyright (C) 2005 Michele Ferretti
    black.bird@tiscali.it
    http://www.blackbirdblog.it
    
    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA   02111-1307, USA.

    XML-RPC supported methods: 
        * getUsersBlogs
        * getUserInfo
        * getPost
        * getRecentPosts
        * newPost
        * editPost
        * deletePost
        * newMediaObject
        * newCategory
        * getCategoryList
        * getPostCategories
        * setPostCategories
        * getTrackbackPings
        * publishPost
        * getPingbacks
        * getTags
        * suggestCategories
        * getComment
        * getComments

    References:
        * http://codex.wordpress.org/XML-RPC_Support
        * http://www.sixapart.com/movabletype/docs/mtmanual_programmatic.html
        * http://docs.python.org/lib/module-xmlrpclib.html
        * http://code.google.com/p/wordpress-library
"""

__author__ = "Theodore Campbell <theodore.campbell@stupidfoot.com>"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2009/04/12 $"
__copyright__ = "Copyright (c) 2009 Theodore Campbell"
__license__ = "LGPL"

import exceptions
import re
import os
import xmlrpclib
import datetime
import time
from pprint import pprint

class WordPressException(exceptions.Exception): #{{{
    """Custom exception for WordPress client operations
    """
    def __init__(self, obj):
        if isinstance(obj, xmlrpclib.Fault):
            self.id = obj.faultCode
            self.message = obj.faultString
        else:
            self.id = 0
            self.message = obj
    
    def __str__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.message)
#}}}
        
class WordPressBlog(object): #{{{
    """Represents blog item
    """ 
    def __init__(self):
        self.id = ''
        self.name = ''
        self.url = ''
        self.isAdmin = False
    def __str__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.name)

    def __repr__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.name)
#}}}
        
class WordPressUser(object): #{{{
    """Represents user item
    """ 
    def __init__(self):
        self.id = ''
        self.firstName = ''
        self.lastName = ''
        self.nickname = ''
        self.email = ''
    def __str__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.name)

    def __repr__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.name)
#}}}
        
class WordPressCategory(object): #{{{
    """Represents category item
    """ 
    def __init__(self):
        self.id = 0
        self.parentId = 0
        self.name = ''
        self.slug = ''
        self.description = ''
        self.rssUrl = ''
        self.htmlUrl = ''
        self.isPrimary = False
    
    def __str__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.name)

    def __repr__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.name)
#}}}

class WordPressComment(object): #{{{
    """Represents comment item
    """ 
    def __init__(self):
        self.id           = 0
        self.userId       = ''
        self.parent       = ''
        self.status       = ''
        self.content      = ''
        self.link         = ''
        self.postId       = 0
        self.postTitle    = ''
        self.author       = ''
        self.authorUrl    = ''
        self.authorEmail  = ''
        self.authorIp     = ''

    def __str__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.content)

    def __repr__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.content)
#}}}

class WordPressPost(object): #{{{
    """Represents post item
    """ 
    def __init__(self):
        self.id = 0
        self.title = ''
        self.date = None
        self.permaLink = ''
        self.description = ''
        self.textMore = ''
        self.excerpt = ''
        self.link = ''
        self.categories = []
        self.user = ''
        self.allowPings = False
        self.allowComments = False
        self.keywords = ''

    def __str__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.title)

    def __repr__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.title)
#}}}

class WordPressTag(object): #{{{
    """Represents tag item
    """ 
    def __init__(self):
        self.id = 0
        self.name = ''
        self.rssUrl = ''
        self.htmlUrl = ''
        self.slug = ''
        self.count = 0
        

    def __str__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.name)

    def __repr__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.name)
#}}}

class WordPressClient(object): #{{{
    """Client for connect to WordPress XML-RPC interface
    """
    
    def __init__(self, url, user, password): #{{{
        self.url = url
        self.user = user
        self.password = password
        self.blogId = 0
        self.categories = None
        self._server = xmlrpclib.ServerProxy(self.url)
    #}}}

    def _filterTag(self, tag): #{{{
        """Transform tag struct in WordPressTag instance 
        """
        tagObj = WordPressTag()
        tagObj.id           = int(tag['tag_id'])
        tagObj.name         = tag['name']
        tagObj.rssUrl       = tag['rss_url']
        tagObj.slug         = tag['slug']
        tagObj.htmlUrl      = tag['html_url']
        tagObj.count        = int(tag['count'])
        return tagObj
    #}}}
 
    def _filterPost(self, post): #{{{
        """Transform post struct in WordPressPost instance 
        """
        postObj = WordPressPost()
        postObj.permaLink       = post['permaLink']
        postObj.description     = post['description']
        postObj.title           = post['title']
        postObj.excerpt         = post['mt_excerpt']
        postObj.user            = post['userid']
        postObj.date            = time.strptime(str(post['dateCreated']), "%Y%m%dT%H:%M:%S")
        postObj.link            = post['link']
        postObj.textMore        = post['mt_text_more']
        postObj.allowComments   = post['mt_allow_comments'] == 1
        postObj.id              = int(post['postid'])
        postObj.categories      = post['categories']
        postObj.allowPings      = post['mt_allow_pings'] == 1
        return postObj
    #}}}

    def _filterComment(self, comment): #{{{
        """Transform comment struct in WordPressComment instance
        """
        commentObj = WordPressComment()
        commentObj.id           = int(comment['comment_id'])
        commentObj.userId       = comment['user_id'] 
        commentObj.parent       = comment['parent'] 
        commentObj.status       = comment['status'] 
        commentObj.content      = comment['content'] 
        commentObj.link         = comment['link'] 
        commentObj.postId       = comment['post_id'] 
        commentObj.postTitle    = comment['post_title'] 
        commentObj.author       = comment['author'] 
        commentObj.authorUrl    = comment['author_url'] 
        commentObj.authorEmail  = comment['author_email'] 
        commentObj.authorIp     = comment['author_ip'] 

        return commentObj
    #}}}

    def _filterCategory(self, cat): #{{{
        """Transform category struct in WordPressCategory instance
        """
        catObj = WordPressCategory()
        if 'categoryId' in cat:
            catObj.id           = int(cat['categoryId'])
            catObj.name         = cat['categoryName'] 
            catObj.description  = cat['categoryDescription'] 
            catObj.htmlUrl      = cat['htmlUrl'] 
            catObj.rssUrl       = cat['rssUrl'] 
            catObj.parentId     = int(cat['parentId'])

        if 'category_id' in cat:
            catObj.id           = int(cat['category_id'])
            catObj.name         = cat['category_name'] 

        if cat.has_key('isPrimary'):
            catObj.isPrimary    = cat['isPrimary']
        return catObj
    #}}}

    def selectBlog(self, blogId): #{{{
        self.blogId = blogId
    #}}}

    def supportedMethods(self): #{{{
        """Get supported methods list
        """
        return self._server.mt.supportedMethods()
    #}}}

    def getLastPost(self): #{{{
        """Get last post
        """
        return tuple(self.getRecentPosts(1))[0]
    #}}}

    def getRecentPosts(self, numPosts=5): #{{{
        """Get recent posts
        """
        try:
            posts = self._server.metaWeblog.getRecentPosts(self.blogId, self.user, 
                                                    self.password, numPosts)
            for post in posts:
                yield self._filterPost(post)    
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}

    def getPost(self, postId): #{{{
        """Get post item
        """
        try:
            return self._filterPost(self._server.metaWeblog.getPost(str(postId), self.user, self.password))
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}

    def getUserInfo(self): #{{{
        """Get user info
        """
        try:
            userinfo = self._server.blogger.getUserInfo('', self.user, self.password)
            userObj = WordPressUser()
            userObj.id = userinfo['userid']
            userObj.firstName = userinfo['firstname']
            userObj.lastName = userinfo['lastname']
            userObj.nickname = userinfo['nickname']
            #userObj.email = userinfo['email']
            return userObj
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}

    def getUsersBlogs(self): #{{{
        """Get blog's users info
        """
        try:
            blogs = self._server.blogger.getUsersBlogs('', self.user, self.password)
            for blog in blogs:
                blogObj = WordPressBlog()
                blogObj.id = blog['blogid']
                blogObj.name = blog['blogName']
                blogObj.isAdmin = blog['isAdmin']
                blogObj.url = blog['url']
                yield blogObj
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}

    def newCategory(self, category): #{{{
        """Add new category
        """
        blogContent = {
            'name': category.name,
            'parent_id': category.parentId,
            'slug': category.slug,
            'description': category.description,
        }
        idNewCat = int(self._server.wp.newCategory(self.blogId, self.user, self.password, blogContent))
        return idNewCat
    #}}}

    def newPost(self, post, publish): #{{{
        """Insert new post
        """
        blogContent = {
            'title' : post.title,
            'description' : post.description,
            'mt_text_more' : post.textMore,
            'mt_keywords': post.keywords,
        }
        blogContent['dateCreated'] = xmlrpclib.DateTime(post.date) 
        # add categories
        i = 0
        categories = []
        for cat in post.categories:
            if i == 0:
                categories.append({'categoryId' : cat, 'isPrimary' : 1})
            else:
                categories.append({'categoryId' : cat, 'isPrimary' : 0})
            i += 1
        
        # insert new post
        idNewPost = int(self._server.metaWeblog.newPost(self.blogId, self.user, self.password, blogContent, 0))
        
        # set categories for new post
        self.setPostCategories(idNewPost, categories)
        
        # publish post if publish set at True 
        if publish:
            self.publishPost(idNewPost)
            
        return idNewPost
    #}}}
    
    def getPostCategories(self, postId): #{{{
        """Get post's categories
        """
        try:
            categories = self._server.mt.getPostCategories(postId, self.user, 
                                                    self.password)
            for cat in categories:
                yield self._filterCategory(cat) 
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}
    
    def setPostCategories(self, postId, categories): #{{{
        """Set post's categories
        """
        self._server.mt.setPostCategories(postId, self.user, self.password, categories)
    #}}}
    
    def editPost(self, postId, post, publish): #{{{
        """Edit post
        """
        blogcontent = {
            'title' : post.title,
            'description' : post.description,
            'permaLink' : post.permaLink,
            'mt_allow_pings' : post.allowPings,
            'mt_text_more' : post.textMore,
            'mt_excerpt' : post.excerpt
        }
        
        if post.date:
            blogcontent['dateCreated'] = xmlrpclib.DateTime(post.date) 
        
        # add categories
        i = 0
        categories = []
        for cat in post.categories:
            if i == 0:
                categories.append({'categoryId' : cat, 'isPrimary' : 1})
            else:
                categories.append({'categoryId' : cat, 'isPrimary' : 0})
            i += 1               
        
        result = self._server.metaWeblog.editPost(postId, self.user, self.password,
                                              blogcontent, 0)
        
        if result == 0:
            raise WordPressException('Post edit failed')
            
        # set categories for new post
        self.setPostCategories(postId, categories)
        
        # publish new post
        if publish:
            self.publishPost(postId)
    #}}}
    
    def deletePost(self, postId): #{{{
        """Delete post
        """
        try:
            return self._server.blogger.deletePost('', postId, self.user, 
                                             self.password)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}
    
    def deleteCategory(self, categoryId): #{{{
        """Delete category
        """
        try:
            return self._server.wp.deleteCategory(self.blogId, self.user,
            categoryId, self.password)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}

    def getCategoryList(self, forceUpdate=False): #{{{
        """Get blog's categories list
        """
        try:
            if self.categories == None or forceUpdate == True:
                self.categories = []
                categories = self._server.wp.getCategories(self.blogId, 
                    self.user, self.password)               
                for cat in categories:
                    self.categories.append(self._filterCategory(cat))   
            return self.categories
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}

    def getCategoryIdFromName(self, name): #{{{
        """Get category id from category name
        """
        for c in self.getCategoryList():
            if c.name == name:
                return c.id
    #}}}
    
    def getTrackbackPings(self, postId): #{{{
        """Get trackback pings of post
        """
        try:
            return self._server.mt.getTrackbackPings(postId)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}
    
    def publishPost(self, postId): #{{{
        """Publish post
        """
        try:
            return (self._server.mt.publishPost(postId, self.user, self.password) == 1)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}
    
    def getPingbacks(self, postUrl): #{{{
        """Get pingbacks of post
        """
        try:
            return self._server.pingback.extensions.getPingbacks(postUrl)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}
    
    def getTags(self): #{{{
        """Get Blog tags
        """
        try:
            tags = self._server.wp.getTags(self.blogId, self.user,
            self.password)

            for tag in tags:
                yield self._filterTag(tag) 
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}

    def newMediaObject(self, mediaFileName): #{{{
        """Add new media object (image, movie, etc...)
        """
        try:
            f = file(mediaFileName, 'rb')
            mediaBits = f.read()
            f.close()
            
            mediaStruct = {
                'name' : os.path.basename(mediaFileName),
                'bits' : xmlrpclib.Binary(mediaBits)
            }
            
            result = self._server.metaWeblog.newMediaObject(self.blogId, 
                                    self.user, self.password, mediaStruct)
            return result['url']
            
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}
    
    def suggestCategories(self, string, maxResults=5): #{{{
        """Suggest Categories
        """
        try:
            cats = self._server.wp.suggestCategories(self.blogId, self.user,
            self.password, string, maxResults)

            for cat in cats:
                yield self._filterCategory(cat)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}

    def getComment(self, commentId): #{{{
        """Get comment.
        """
        try:
            return self._filterComment(self._server.wp.getComment(self.blogId,
            self.user, self.password, commentId))
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}

    def getComments(self, status='approve', post_id=0, number=10, offset=0): #{{{
        """Get comments.
        """
        struct = dict()
        struct['status']    = status
        struct['post_id']   = post_id
        struct['number']    = number
        struct['offset']    = offset 
        try:
            comments = self._server.wp.getComments(self.blogId, self.user,
            self.password, struct)

            for comment in comments:
                yield self._filterComment(comment)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
    #}}}


#}}}

