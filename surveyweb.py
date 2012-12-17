import webapp2
from google.appengine.api import users
import os
import cgi
import datetime
from google.appengine.ext.webapp import template
from google.appengine.ext import db
import random
from xml.dom.minidom import parse
from xml.dom.minidom import Document
from xml.dom.minidom import parse, parseString
import re

class CategoryInfo(db.Model):
    """Models an individual category entry."""
    category_name = db.StringProperty()
    created_by = db.StringProperty()
    createdate = db.DateTimeProperty(auto_now_add=True)
    expirydate = db.DateTimeProperty()
class MyModel(db.Model):
    data = db.BlobProperty(required=True)
    mimetype = db.StringProperty(required=True)
    
class Comments(db.Model):
    """Models an Comments entry."""
    item = db.StringProperty()
    item_comment = db.StringProperty()
    icategory_name = db.StringProperty()
    icreated_by = db.StringProperty()

class UserName(db.Model):
    """Models an Username entry."""
    username=db.UserProperty()

class ItemInfo(db.Model):
    """Models an ItemInfo entry."""
    item_name = db.StringProperty()
    icategory_name = db.StringProperty()
    icreated_by = db.StringProperty()
    
class VoteResults(db.Model):
    """Models an VoteResults entry."""
    vitem_won = db.StringProperty()
    vitem_lost = db.StringProperty()
    vcategory_name = db.StringProperty()
    vusername = db.StringProperty()
        
    
class MenuSelect(webapp2.RequestHandler):
    def get(self): 
        if(self.request.get('menu_choice') == '1'):
            self.redirect('/createcategory?')

        elif(self.request.get('menu_choice') == '2'):
            self.redirect('/createitem?')
               
        elif(self.request.get('menu_choice') == '5'):
            self.redirect('/browseitems?')
            
        elif(self.request.get('menu_choice') == '6'):
            self.redirect('/vote?')

        elif(self.request.get('menu_choice') == '7'):
            self.redirect('/resultcategory?')
            
        elif(self.request.get('menu_choice') == '8'):
            self.redirect('/search?')
        
        elif(self.request.get('menu_choice') == '9'):
            self.redirect('/exportxml?')
        
        elif(self.request.get('menu_choice') == '10'):
            self.redirect('/importxml?')
            
        elif(self.request.get('menu_choice') == '11'):
            self.redirect('/addcomment?')
       
        else:
            self.redirect('/?menu_choice=0')
            
class MainPage(webapp2.RequestHandler):
# Main Page for the , using index.html to render webpage
    def get(self):
        
        menu_choice = self.request.get('menu_choice')
        user = users.get_current_user()
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            useremail = user.email()
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'menu_choice':menu_choice,
            'url': url,
            'user': user,
            'url_linktext': url_linktext,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

#Class used to export webpage , uses export.html to render webpage         
class BrowseExport(webapp2.RequestHandler):

    def get(self):
           user = users.get_current_user()
           if users.get_current_user():
                url = users.create_logout_url(self.request.uri)
                url_linktext = 'Logout'
                BackToMenu = self.request.get('BackToMenu')   
                AddItem     = self.request.get('AddItem')
                ## check if back button is pressed
                if (BackToMenu != ''):
                    self.redirect('/')
                categories_val = db.GqlQuery("SELECT * FROM CategoryInfo ")
             
           else:
                url = users.create_login_url(self.request.uri)
                url_linktext = 'Login'
                categories_val=" "
                 
           template_values = {
                 'categories_val': categories_val,
                 'url': url,
                 'user': user,
                 'url_linktext': url_linktext,
             }
 
           path = os.path.join(os.path.dirname(__file__), 'exportxml.html')
           self.response.out.write(template.render(path, template_values)) 
 

#Class used to export webpage , uses export.html to render webpage            
class Export(webapp2.RequestHandler):
    def get(self):
        BackToMenu = self.request.get('BackToMenu')   
        ViewXML     = self.request.get('ViewXML')
        if (BackToMenu != ''):
                    self.redirect('/')
        else:
            self.response.headers['Content-Type'] = 'text/xml'
            category_name=self.request.get('category_name')
            uname  = self.request.get('categorycreator') 
            items = db.GqlQuery("SELECT * FROM ItemInfo WHERE icategory_name = :1 and icreated_by = :2",category_name,uname) 
            doc = Document()
            category = doc.createElement("CATEGORY")
            doc.appendChild(category)
            name1=doc.createElement("NAME")
            category.appendChild(name1)
            text=doc.createTextNode(category_name)
            name1.appendChild(text)
            for i in items.run():
                item = doc.createElement("ITEM")
                category.appendChild(item)
                name = doc.createElement("NAME")
                item.appendChild(name)
                ntext = doc.createTextNode(i.item_name)
                name.appendChild(ntext)
        
            self.response.out.write(doc.toprettyxml())

#Class used to import webpage , uses importxml.html to render webpage              
class Import(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            BackToMenu = self.request.get('BackToMenu')   
            useremail = user.email()

        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        
        template_values = {
            'url': url,
            'user': user,
            'url_linktext': url_linktext,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'importxml.html')
        self.response.out.write(template.render(path, template_values)) 
        
 
#Class used to import webpage , uses importxml.html to render webpage
class Import1(webapp2.RequestHandler):
    def post(self):
        self.response.out.write("<link rel=\"stylesheet\" type=\"text/css\"  href=\"/stylesheets/style.css\" media=\"screen\" />")
        self.response.out.write("<div id=\"page\">")
        self.response.out.write('<H1>Imported Items</H1>')
        BackToMenu = self.request.get('BackToMenu') 
        user = users.get_current_user()  
        useremail = user.email()
        if (BackToMenu != ''):
            self.redirect('/')
        submit=self.request.get('submit')

        if (submit != ''):
                 data1=self.request.POST.multi['file'].file.read()
                 count=0
                 data=parseString(data1)
                 errorcode=0
                 xmlTag = data.getElementsByTagName('CATEGORY')
                 for i in xmlTag:
                     name = i.getElementsByTagName('NAME')
                     for j in name:
                       if count==0:
                           category=j.firstChild.data
                           categorycheck = db.GqlQuery("SELECT * FROM CategoryInfo WHERE category_name = :1 and created_by = :2",category,user.email())
                           if (categorycheck.count() == 0):
                               self.response.out.write("Categories Imported:    ")
                               self.response.out.write("<br>")
                               self.response.out.write(j.firstChild.data) 
                               self.response.out.write("<br>")
                               self.response.out.write("<br>")
                               categoryvalue=CategoryInfo()
                               categoryvalue.category_name=j.firstChild.data
                               categoryvalue.created_by=user.email()
                               categoryvalue.expirydate=categoryvalue.createdate+datetime.timedelta(days=10, hours=0)
                               categoryvalue.put()
                                 
                               self.response.out.write("Items Imported: ") 
                               self.response.out.write("<br>")
                           else:
                               errorcode=100
                               self.response.out.write("Category already exists, Cannot add ")
                               self.response.out.write(j.firstChild.data)
                           count=count+1     
                       else:
                           if (errorcode != 100):
                               self.response.out.write(j.firstChild.data) 
                               self.response.out.write("<br>") 
                               categoryobj=CategoryInfo(key_name=category) 
                               itemvalue=ItemInfo(parent=categoryobj,key_name=j.firstChild.data)
                               itemvalue.item_name=j.firstChild.data
                               itemvalue.icategory_name=category
                               itemvalue.icreated_by=user.email()
                               itemvalue.put()
#Class used to Vote Items 
class VoteItem(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<link rel=\"stylesheet\" type=\"text/css\"  href=\"/stylesheets/style.css\" media=\"screen\" />")
        self.response.out.write("<div id=\"page\">")
        self.response.out.write('<H1>Vote</H1>')
        BrowseSurvey = self.request.get('Browse')
   # check user login
        user = users.get_current_user()
        
        if user:    # signed in already
            self.response.out.write('Hello <em>%s</em>! [<a href="%s">sign out</a>]' % (
                user.email(), users.create_logout_url(self.request.uri)))
            self.response.out.write('</br>')
            categories_val = db.GqlQuery("SELECT * FROM CategoryInfo ")
            self.response.out.write("<br/>")
            self.response.out.write("<br/>")
            self.response.out.write(" Category Name :  Creator")
            self.response.out.write("<br/>")
            self.response.out.write("<br/>")
            ## get selection values
            BackToMenu = self.request.get('BackToMenu')
            BrowseSurvey = self.request.get('Browse')         
 
            ## check if back button is pressed
            if (BackToMenu != ''):
                self.redirect('/')
 
                       
            self.response.out.write('<form action="/pickitem?%s" method="get">')
            for categories in categories_val:
              self.response.out.write('<div><input type="radio" name="category_name" value="%s#%s" checked>%s     : %s</div>' % (categories.category_name, categories.created_by,  categories.category_name, categories.created_by ))
            self.response.out.write("""
                <div>
                    <input type="submit" name="BackToMenu" value="Back to Menu">
                    <input type="submit" name="VoteItem" value="Vote Item">
                </div>
            """)
            #### End General Code  ####

        else:    # let user choose authenticator
            self.response.out.write('<br><FONT Size=4><em><b>Please sign in to access the category app!!! <br><br>Sign in using:</b></em></FONT>')
            self.redirect(users.create_login_url(self.request.uri))
        self.response.out.write("</div>") 

#Class used to choose items and show the counts for category
class PickItem(webapp2.RequestHandler):
    def get(self):
     user = users.get_current_user()
     self.response.out.write("<link rel=\"stylesheet\" type=\"text/css\"  href=\"/stylesheets/style.css\" media=\"screen\" />")
     self.response.out.write("<div id=\"page\">")
     self.response.out.write('<H1>Vote</H1>')
     categorycreator = self.request.get('categorycreator')   
     categoryname = self.request.get('category_name')
     words = categoryname.split("#")
     count1=0
     for m in words:
      if(count1 == 0):
       categoryname = m
       self.response.out.write("<br>")
       count1 = count1+1
      else:
       categorycreator=m
       currentdatetime=datetime.datetime.now()
     categories1 = db.GqlQuery("SELECT * FROM ItemInfo WHERE icategory_name = :1 and icreated_by = :2",categoryname,categorycreator)
     categories2 = db.GqlQuery("SELECT * FROM CategoryInfo WHERE category_name = :1 and created_by = :2",categoryname,categorycreator)
 
     BackToMenu = self.request.get('BackToMenu')
     VoteItem = self.request.get('VoteItem')
     VoteItem1 = self.request.get('VoteItem1')
     SkipItem=self.request.get('SkipItem')
     item_name=self.request.get('item_name')
     
     if (BackToMenu != ''):
                self.redirect('/')
     if(VoteItem1 != ''): 
             item_name=self.request.get('item_name') 
             item1=self.request.get('item1') 
             item2=self.request.get('item2')     
             if(item_name == item1):
                 vitem=VoteResults()
                 vitem.vitem_won = item1
                 vitem.vitem_lost = item2
                 won=item1
                 lost=item2
                 vitem.vcategory_name = categoryname
                 vitem.vusername = categorycreator
                 vitem.put()
             else:
                 vitem=VoteResults()
                 vitem.vitem_won = item2
                 vitem.vitem_lost = item1
                 won=item2
                 lost=item1
                 vitem.vcategory_name = categoryname
                 vitem.vusername = categorycreator 
                 vitem.put()
             countwon=0
             countlost=0
             itemswon = db.GqlQuery("SELECT * FROM VoteResults WHERE vcategory_name = :1 and vusername = :2 and vitem_won = :3  ",categoryname,categorycreator, won)
             itemslost = db.GqlQuery("SELECT * FROM VoteResults WHERE vcategory_name = :1 and vusername = :2 and vitem_won = :3  ",categoryname,categorycreator, lost)
             for m in itemswon:
                 countwon=countwon+1
             for n in itemslost:
                 countlost=countlost+1 
             self.response.out.write("You voted for")
             self.response.out.write("\"")    
             self.response.out.write(vitem.vitem_won)
             self.response.out.write("\"")
             self.response.out.write("over")
             self.response.out.write("\"")
             self.response.out.write(vitem.vitem_lost)
             self.response.out.write("\"")
             self.response.out.write("</i>")
             self.response.out.write("</br>")
             self.response.out.write("</br>")
             self.response.out.write("\nCurrent totals:")
             self.response.out.write("<table border=\"1\">")                      
             self.response.out.write("<tr>")
             self.response.out.write( "<th>")
             self.response.out.write(won)
             self.response.out.write( "</th>")
             self.response.out.write("<th>")
             self.response.out.write(lost)
             self.response.out.write("</th>")
             self.response.out.write("</tr>")
             self.response.out.write("<tr>")
             self.response.out.write("<th>")
             self.response.out.write(countwon)
             self.response.out.write("</th>")
             self.response.out.write("<th>")
             self.response.out.write(countlost)
             self.response.out.write("</th>")
             self.response.out.write("</tr>")
             self.response.out.write( "</table>")
             
             list=[]
             abc=[]
             counta =0         
             for category in categories1:
                 list.append(category.item_name)
                 counta= counta+1 
             if( counta < 2):
                 self.response.out.write("Less then2 items, Voting cannot happen")
             else: 
                 abc=random.sample(list, 2)   
                 self.response.out.write("Category : ")
                 self.response.out.write(categoryname)
                 self.response.out.write('<form action="/pickitem?%s" method="get">')
                 self.response.out.write('<div><input type="radio" name="item_name" value="%s" checked>%s  </div>' %(abc[0],abc[0]))
                 self.response.out.write('<div><input type="radio" name="item_name" value="%s" >%s  </div>' %(abc[1],abc[1]))
                 self.response.out.write("""<input type=hidden name=categorycreator value="%s">""" % (categorycreator))
                 self.response.out.write("""<input type=hidden name=category_name value="%s">""" % (categoryname)) 
                 self.response.out.write("""<input type=hidden name=item1 value="%s">""" % abc[0]) 
                 self.response.out.write("""<input type=hidden name=item2 value="%s">""" % abc[1]) 
                 self.response.out.write("""
                  <div>
                <input type="submit" name="BackToMenu" value="Back to Menu">
                <input type="submit" name="VoteItem1" value="Vote Item1">
                <input type="submit" name="SkipItem" value="Skip Item">
                </div>
                """)
     if(VoteItem != ''):
             list=[]
             abc=[]
             counta =0
             for category in categories1:
                 list.append(category.item_name)
                 counta= counta+1                 
             if( counta < 2):
                 self.response.out.write("Less then2 items, Voting cannot happen")
             else:
                 abc=random.sample(list, 2)   
                 self.response.out.write("Category : ")
                 self.response.out.write(categoryname)
                 self.response.out.write('<form action="/pickitem?%s" method="get">')
                 self.response.out.write('<div><input type="radio" name="item_name" value="%s" checked>%s  </div>' %(abc[0],abc[0]))
                 self.response.out.write('<div><input type="radio" name="item_name" value="%s" >%s  </div>' %(abc[1],abc[1]))
                 self.response.out.write("""<input type=hidden name=categorycreator value="%s">""" % (categorycreator))
                 self.response.out.write("""<input type=hidden name=category_name value="%s">""" % (categoryname)) 
                 self.response.out.write("""<input type=hidden name=item1 value="%s">""" % abc[0]) 
                 self.response.out.write("""<input type=hidden name=item2 value="%s">""" % abc[1]) 
                 self.response.out.write("""
                <div>
                <input type="submit" name="BackToMenu" value="Back to Menu">
                <input type="submit" name="VoteItem1" value="Vote Item">
                <input type="submit" name="SkipItem" value="Skip Item">
                </div>
                """)
     if(SkipItem != ''):
             list=[]
             abc=[]
             
             for category in categories1:
                 list.append(category.item_name)
             abc=random.sample(list, 2)   
             self.response.out.write("Category : ")
             self.response.out.write(categoryname)
             self.response.out.write('<form action="/pickitem?%s" method="get">')
             self.response.out.write('<div><input type="radio" name="item_name" value="%s" checked>%s  </div>' %(abc[0],abc[0]))
             self.response.out.write('<div><input type="radio" name="item_name" value="%s" >%s  </div>' %(abc[1],abc[1]))
             self.response.out.write("""<input type=hidden name=categorycreator value="%s">""" % (categorycreator))
             self.response.out.write("""<input type=hidden name=category_name value="%s">""" % (categoryname)) 
             self.response.out.write("""<input type=hidden name=item1 value="%s">""" % abc[0]) 
             self.response.out.write("""<input type=hidden name=item2 value="%s">""" % abc[1]) 
             self.response.out.write("""
              <div>
            <input type="submit" name="BackToMenu" value="Back to Menu">
            <input type="submit" name="VoteItem1" value="Vote Item1">
            <input type="submit" name="SkipItem" value="Skip Item">
            </div>
            """)

        
     self.response.out.write("</div>") 

#Class used to Add Comments to Items 
class AddComments(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<link rel=\"stylesheet\" type=\"text/css\"  href=\"/stylesheets/style.css\" media=\"screen\" />")
        self.response.out.write("<div id=\"page\">")
        self.response.out.write('<H1>Vote</H1>')
        BrowseSurvey = self.request.get('Browse')
   # check user login
        user = users.get_current_user()
        
        if user:    # signed in already
            self.response.out.write('Hello <em>%s</em>! [<a href="%s">sign out</a>]' % (
                user.email(), users.create_logout_url(self.request.uri)))
            self.response.out.write('</br>')
            categories_val = db.GqlQuery("SELECT * FROM CategoryInfo ")
            self.response.out.write("<br/>")
            self.response.out.write("<br/>")
            self.response.out.write(" Category Name :  Creator")
            self.response.out.write("<br/>")
            self.response.out.write("<br/>")
            ## get selection values
            BackToMenu = self.request.get('BackToMenu')
            BrowseSurvey = self.request.get('Browse')         
 
            ## check if back button is pressed
            if (BackToMenu != ''):
                self.redirect('/')
 
                       
            self.response.out.write('<form action="/itemtocomment?%s" method="get">')
            for categories in categories_val:
              self.response.out.write('<div><input type="radio" name="category_name" value="%s#%s"  checked>%s     : %s</div>' % (categories.category_name,categories.created_by,  categories.category_name, categories.created_by ))
              self.response.out.write("""<input type=hidden name=categoryexpiry value="%s">""" % (categories.expirydate))
            self.response.out.write("""
                <div>
                    <input type="submit" name="BackToMenu" value="Back to Menu">
                    <input type="submit" name="VoteItem" value="Vote Item">
                </div>
            """)
            #### End General Code  ####

        else:    # let user choose authenticator
            self.response.out.write('<br><FONT Size=4><em><b>Please sign in to access the category app!!! <br><br>Sign in using:</b></em></FONT>')
            self.redirect(users.create_login_url(self.request.uri))

        self.response.out.write("</div>")

class ItemComments(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<link rel=\"stylesheet\" type=\"text/css\"  href=\"/stylesheets/style.css\" media=\"screen\" />")
        self.response.out.write("<div id=\"page\">")
        self.response.out.write('<H1>Add Comments</H1>')
        BackToMenu = self.request.get('BackToMenu')
        AddItem     = self.request.get('AddItem')  
        if (BackToMenu != ''):
                self.redirect('/')
        category_name = self.request.get('category_name')
        words = category_name.split("#")
        count1=0
        for m in words:
         if(count1 == 0):
            category_name = m
            self.response.out.write("<br>")
            count1 = count1+1
         else:
            createdcategory=m
        
        if (AddItem != ''):
            comments = self.request.get("comments")  
            item_name=self.request.get("item_name")
            commentvalue=Comments()
            words =item_name.split("#")
            count=0
            for q in words:
              if count==0:
                  item_name=q
              if count==1:
                  category_name=q
              if count==2:
                  createdcategory=q
              count=count+1
               
            commentvalue.item = item_name
            commentvalue.item_comment = self.request.get("comments")
            commentvalue.icategory_name = category_name
            commentvalue.icreated_by =   createdcategory
            commentvalue.put()
            self.response.out.write("Comments Succesfully added")
            self.response.out.write("<br>")
        items2 = db.GqlQuery("SELECT * FROM ItemInfo where icategory_name = :1 and icreated_by = :2 ",category_name,createdcategory)
        self.response.out.write("Categories:")
        self.response.out.write("category_name")
        self.response.out.write('<form action="/itemtocomment?%s" method="get">')
        for items3 in items2:
            self.response.out.write('<div><input type="radio" name="item_name" value="%s#%s#%s" checked>%s    </div>' % (items3.item_name, items3.icategory_name, items3.icreated_by ,   items3.item_name ))
        self.response.out.write('Add Comments to the item: <input type="text" name="comments" size ="25">') 
        self.response.out.write("""
            <div>
                <input type="submit" name="AddItem" value="AddItem">
            </div>
           """)
        self.response.out.write("</div>")
        
#Class to Create Items, and throws error is number of items field populated with space or
#alphabet
class CreateItems1(webapp2.RequestHandler): 
    def get(self): 
       user = users.get_current_user()
       erroroccured=0
       if users.get_current_user():
                url = users.create_logout_url(self.request.uri)
                url_linktext = 'Logout'
                category_name=self.request.get('category_name')
                createitems = self.request.get('createitems')  
                BackToMenu  =  self.request.get('BackToMenu')
                sitem = []
                if not  (self.request.get('items')):
                     erroroccured=100
                try:
                    items = int(cgi.escape(self.request.get('items')))
                    for itemsin in range(1,items+1):
                        sitem.append(itemsin)
                   
                except ValueError:
                    erroroccured=101
                    items=[]
             
                if (BackToMenu != ''):
                    self.redirect('/')
                
                if  (createitems != ''):

                    category_name=self.request.get('categoryname')
                    
                    user = users.get_current_user()
 
                    user = users.get_current_user()
                    
                    for cntr in range(1,items+1):
                       currentitem="items" + str(cntr)
                       additem =(self.request.get(currentitem))
                       categoryobj=CategoryInfo(key_name=category_name)
                       itemvalue=ItemInfo(parent=categoryobj,key_name=additem)
                       itemvalue.item_name=additem
                       itemvalue.icategory_name=category_name
                       itemvalue.icreated_by=user.email()
                       itemvalue.put()
                   
       else:
                url = users.create_login_url(self.request.uri)
                url_linktext = 'Login'  
                self.redirect(users.create_login_url(self.request.uri))
                
              
       template_values = {
                                        'url': url,
                                        'user': user,
                                        'url_linktext': url_linktext,
                                        'category_name' :category_name,
                                        'items' : items,
                                        'erroroccured' : erroroccured,
                                        'sitem': sitem,
                    }
        
       path = os.path.join(os.path.dirname(__file__), 'createitem1.html')
       self.response.out.write(template.render(path, template_values))
            
 #Class to Create Items, and throws error is number of items field populated with space or
#alphabet           
class CreateItems(webapp2.RequestHandler): 
    def get(self): 
            user = users.get_current_user()
            if users.get_current_user():
                url = users.create_logout_url(self.request.uri)
                url_linktext = 'Logout'
                BackToMenu = self.request.get('BackToMenu')   
                AddItem     = self.request.get('AddItem')
                ## check if back button is pressed
                if (BackToMenu != ''):
                    self.redirect('/')
                categories_val = db.GqlQuery("SELECT * FROM CategoryInfo WHERE created_by = :1 ",user.email())
                   
                template_values = {
                 'categories_val': categories_val,
                 'url': url,
                 'user': user,
                 'url_linktext': url_linktext,
                 }
             
                path = os.path.join(os.path.dirname(__file__), 'createitem.html')
                self.response.out.write(template.render(path, template_values))  
            else:
                url = users.create_login_url(self.request.uri)
                url_linktext = 'Login'
           
#Class to Create Categorys, and throws error if Category already exists
class CreateCategory(webapp2.RequestHandler):
    
    def get(self): 
 
        user = users.get_current_user()
        errorvalue=0
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            useremail = user.email()
            url_linktext = 'Logout'
            usercheck = db.GqlQuery("SELECT * FROM UserName WHERE username = :1",user)
        
            if(usercheck.count() == 0):
                usernameobj=UserName(key_name=user.email())
                usernameobj.username=user
                usernameobj.put()
            else:
                usernameobj=UserName(key_name=user.email())
            self.response.out.write('</br>')
            ## get selection values
            self.response.out.write('</br>')
            category_name = self.request.get('category_name')
            BackToMenu = self.request.get('BackToMenu')
            Next = self.request.get('Next')
            if (BackToMenu != ''):
                self.redirect('/')
                
            if (Next != ''):
                if (category_name != ''):
            ## check if back button is pressed
                    categories = db.GqlQuery("SELECT * FROM CategoryInfo WHERE category_name = :1 and created_by = :2",category_name,user.email())
                    if(categories.count() > 0):
                       self.response.out.write(user)
                       errorvalue=100
                    else:
                       expiry_day = int(cgi.escape(self.request.get('day')))
                       expiry_hours= int(cgi.escape(self.request.get('hours')))
                       categoryvalue=CategoryInfo(parent=usernameobj)
                       categoryvalue.category_name=category_name
                       categoryvalue.created_by=user.email()
                       categoryvalue.expirydate=categoryvalue.createdate+datetime.timedelta(days=expiry_day, hours=expiry_hours)
                       categoryvalue.put()
            
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            
        template_values = {
            'url': url,
            'user': user,
            'url_linktext': url_linktext,
            'errorvalue' :errorvalue
        }
        
        path = os.path.join(os.path.dirname(__file__), 'createcategory.html')
        self.response.out.write(template.render(path, template_values))
        
#Class to Crender the Results for the category in sorted order , it also incudes
#advance feature of comments
class ResultItem(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<link rel=\"stylesheet\" type=\"text/css\"  href=\"/stylesheets/style.css\" media=\"screen\" />")
        self.response.out.write("<div id=\"page\">")
        self.response.out.write('<H1>Vote</H1>')
        BrowseSurvey = self.request.get('Browse')
   # check user login
        user = users.get_current_user()
        
        if user:    # signed in already
            self.response.out.write('Hello <em>%s</em>! [<a href="%s">sign out</a>]' % (
                user.email(), users.create_logout_url(self.request.uri)))
            self.response.out.write('</br>')
            categories_val = db.GqlQuery("SELECT * FROM CategoryInfo ")
            self.response.out.write("<br/>")
            self.response.out.write("<br/>")
            self.response.out.write(" Category Name :  Creator")
            self.response.out.write("<br/>")
            self.response.out.write("<br/>")
            ## get selection values
            BackToMenu = self.request.get('BackToMenu')
            ## check if back button is pressed
            if (BackToMenu != ''):
                self.redirect('/')
 
                       
            self.response.out.write('<form action="/showresult?%s" method="get">')
            for categories in categories_val:
              self.response.out.write('<div><input type="radio" name="category_name" value="%s#%s" checked>%s     : %s</div>' % (categories.category_name,categories.created_by,  categories.category_name, categories.created_by ))
            self.response.out.write("""
                <div>
                    <input type="submit" name="BackToMenu" value="Back to Menu">
                    <input type="submit" name="ResultItem" value="Results">
                </div>
            """)
            #### End General Code  ####

        else:    # let user choose authenticator
            self.response.out.write('<br><FONT Size=4><em><b>Please sign in to access the category app!!! <br><br>Sign in using:</b></em></FONT>')
            self.redirect(users.create_login_url(self.request.uri))

        self.response.out.write("</div>") 

class Search(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<link rel=\"stylesheet\" type=\"text/css\"  href=\"/stylesheets/style.css\" media=\"screen\" />")
        self.response.out.write("<div id=\"page\">")
        self.response.out.write('<H1>Search</H1>')
        self.response.out.write("""<form name='searchform' action='/search1' method='get'><div align=middle><h3>Search for a Item or Category:- <br><input type='text' name='searchword'><br><input type='submit' value='Search'> </h3></div></form>""") 
        self.response.out.write("</div>")
        
class Search1(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<link rel=\"stylesheet\" type=\"text/css\"  href=\"/stylesheets/style.css\" media=\"screen\" />")
        self.response.out.write("<div id=\"page\">")
        self.response.out.write('<H1>Search</H1>')
        searchword = (self.request.get('searchword')) 
        dbcategory = db.GqlQuery("SELECT * "
                            "FROM CategoryInfo "  )
        
        dbitem = db.GqlQuery("SELECT * "
                            "FROM ItemInfo " )
        searchcount = {}
        sortsearchcount = {}
        s=0
        q=0
        for search1  in dbcategory:
            if(searchword in search1.category_name):
                s=s+1 
        for search2  in dbitem:
            if(searchword in search2.item_name):
                q=q+1 
        self.response.out.write('<H3>Category Search</H3>')
        if s == 0:
          self.response.out.write("No Categories Matched that Category")  
        else:
          self.response.out.write("<table border=\"1\">")
          self.response.out.write("<tr>")
          self.response.out.write("<th>")
          self.response.out.write("Category")
          self.response.out.write("</th>")
          self.response.out.write("<th>")
          self.response.out.write("Created by ")
          self.response.out.write("</th>")
          self.response.out.write("<th>")
          self.response.out.write("Created date ")
          self.response.out.write("</th>")
          self.response.out.write("<th>")
          self.response.out.write("Expiry date ")
          self.response.out.write("</th>")
          self.response.out.write( "</tr>")
          for search1  in dbcategory:
            if(searchword in search1.category_name):
                self.response.out.write("<tr>")
                self.response.out.write("<td>")
                self.response.out.write(search1.category_name)
                self.response.out.write("</td>")
                self.response.out.write("<td>")
                self.response.out.write(search1.created_by)
                self.response.out.write("</td>")
                self.response.out.write("<td>")
                self.response.out.write(search1.createdate)
                self.response.out.write("</td>")
                self.response.out.write("<td>")
                self.response.out.write(search1.expirydate)
                self.response.out.write("</td>")
                self.response.out.write("</tr>") 
        self.response.out.write("</table>")
        self.response.out.write('<H3>Item Search</H3>')
        if q == 0:
            self.response.out.write("No Items Matched that Items")  
        else:
            self.response.out.write("<table border=\"1\">")
            self.response.out.write("<tr>")
            self.response.out.write("<th>")
            self.response.out.write("Items")
            self.response.out.write("</th>")
            self.response.out.write("<th>")
            self.response.out.write("Category Name ")
            self.response.out.write("</th>")
            self.response.out.write("<th>")
            self.response.out.write("Created by ")
            self.response.out.write("</th>")
            self.response.out.write( "</tr>")
            for search2  in dbitem:
                if(searchword in search2.item_name):
                    self.response.out.write("<tr>")
                    self.response.out.write("<td>")
                    self.response.out.write(search2.item_name)
                    self.response.out.write("</td>")
                    self.response.out.write("<td>")
                    self.response.out.write(search2.icategory_name)
                    self.response.out.write("</td>")
                    self.response.out.write("<td>")
                    self.response.out.write(search2.icreated_by)
                    self.response.out.write("</td>")
                    self.response.out.write("</tr>") 
            self.response.out.write("</table>")
        self.response.out.write("</div>")
        
                        
class ShowResult(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<link rel=\"stylesheet\" type=\"text/css\"  href=\"/stylesheets/style.css\" media=\"screen\" />")
        self.response.out.write("<div id=\"page\">")
        self.response.out.write('<H1>Results</H1>')
        category_name = self.request.get('category_name')
        words = category_name.split("#")
        count1=0
        for m in words:
            if(count1 == 0):
                category_name = m
                self.response.out.write("<br>")
                count1 = count1+1
            else:
                createdcategory=m
                
        currentdatetime=datetime.datetime.now()
        totalitems   = db.GqlQuery("SELECT * FROM ItemInfo WHERE icategory_name = :1 and icreated_by = :2 ",category_name,createdcategory)
        a=[]
        self.response.out.write("<table border=\"1\">")
        self.response.out.write("<tr>")
        self.response.out.write("<th>")
        self.response.out.write("Item ")
        self.response.out.write("</th>")
        self.response.out.write("<th>")
        self.response.out.write("For ")
        self.response.out.write("</th>")
        self.response.out.write("<th>")
        self.response.out.write("Against ")
        self.response.out.write( "</th>")
        self.response.out.write( "<th>")
        self.response.out.write( "Percentage ")
        self.response.out.write( "</th>")
        self.response.out.write( "<th>")
        self.response.out.write( "Comments ")
        self.response.out.write( "</th>")
        self.response.out.write( "</tr>")
        for items in totalitems:
          a.append(items.item_name)
        student_tuples = []
        for sa in a:
          countwon=0.0
          countlost=0.0
          percentage=0.0 
          itemswon = db.GqlQuery("SELECT * FROM VoteResults WHERE vcategory_name = :1 and vusername = :2 and vitem_won = :3  ",category_name,createdcategory,sa)
          itemslost = db.GqlQuery("SELECT * FROM VoteResults WHERE vcategory_name = :1 and vusername = :2 and vitem_lost = :3  ",category_name,createdcategory,sa)
          itemcomments =db.GqlQuery("SELECT * FROM Comments  WHERE icategory_name = :1 and icreated_by = :2 and item = :3",category_name,createdcategory,sa)
          out_str = " "
          for itemiter in itemcomments:            
              out_str += str(itemiter.item_comment)+","
          for  itemsa in itemswon:
            countwon=countwon+1
          for  itemsb in itemslost:
            countlost=countlost+1
            
          if(countwon == 0 and countlost == 0):
              percentage = -1000
          else:
              percentage = (countwon)/(countwon+countlost) * 100.0    
          values=(sa,countwon,countlost,percentage,out_str)
          student_tuples.append(values)
         
        s1=sorted(student_tuples, key=lambda student: student[3]) 
        for s in reversed(s1):
           item = s[0]
           won=  s[1]
           lost =  s[2]
           if(s[3] == -1000):
            perc = "-"
           else:
            perc = s[3]
           comments = s[4]
           self.response.out.write("<tr>")
           self.response.out.write("<td>")
           self.response.out.write(item)
           self.response.out.write("</td>")
           self.response.out.write("<td>")
           self.response.out.write(won)
           self.response.out.write("</td>")
           self.response.out.write("<td>")
           self.response.out.write(lost)
           self.response.out.write("</td>")
           self.response.out.write("<td>")
           self.response.out.write(perc)
           self.response.out.write("</td>")
           self.response.out.write("<td>")
           self.response.out.write(comments)
           self.response.out.write("</td>")
           self.response.out.write("</tr>")
           self.response.out.write("<br>") 
        self.response.out.write("</table>")
        self.response.out.write("</div>")          
       
        

app = webapp2.WSGIApplication(
                                    [('/', MainPage),
                                     ('/menuselect', MenuSelect),
                                     ('/createcategory', CreateCategory),
                                     ('/createitem', CreateItems),
                                     ('/createitem1', CreateItems1),
                                     ('/vote',VoteItem),
                                     ('/pickitem',PickItem),
                                     ('/resultcategory',ResultItem),
                                     ('/showresult',ShowResult),
                                     ('/addcomment',AddComments),
                                     ('/itemtocomment',ItemComments),
                                     ('/search',Search),
                                     ('/search1',Search1),
                                     ('/exportxml',BrowseExport),
                                     ('/exportxml1',Export),
                                     ('/importxml',Import),
                                     ('/importxml1',Import1)],
                                     debug=True)
