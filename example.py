#!/usr/bin/env python

"""
    Small example script that publish post with JPEG image
"""

# import library
import yawpl

print 'Example of posting.'
print

wordpress = raw_input('Wordpress URL:')
user = raw_input('Username:')
password = raw_input('Password:')

# prepare client object
wp = yawpl.WordPressClient(wordpress, user, password)

# select blog id
wp.selectBlog(0)
    
# upload image for post
imageSrc = wp.newMediaObject('python.jpg')

if imageSrc:
    # create post object
    post = wordpresslib.WordPressPost()
    post.title = 'Test post'
    post.description = '''
    Python is the best programming language in the earth !
    
    <img src="%s" />
    
    ''' % imageSrc
    post.categories = (wp.getCategoryIdFromName('Python'),)
    
    # pubblish post
    idNewPost = wp.newPost(post, True)
    
    print
    print 'posting successfull!'
    

