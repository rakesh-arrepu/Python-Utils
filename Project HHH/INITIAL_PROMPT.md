# Initial Prompt

Persona: Tech Architect 

You are a Tec Architect and want to create a product having the below items. The purpose of the product is to create a group and add members in it. Each member can add 3 sections daily which are mandate.
Sections are as below:
1. Health
2. Happiness
3. Hela

There should be info icon and provide info on each section with example on how & what to fill in the section.
Each section should have status bar indicating the section is filled or not.
There should be a status bar on to of the screen to view the progress of filing data in each section
The data should be filled day wise. Each day should consists of one record for all 3 sections. 
user can modify data but can't have more than 1 record per day for each section.
There should be 'day counter'- which counts the day when user fills all the sections for any given day the counter will increment to ONE.
There should be REST API's involved to Create, Get, Edit data.

Groups:
Create group, Edit group, Delete Group
 - Admin for Group-  admin role should have delete , Edit permissions. 
 - Other users in Group- Only read access
 - Admin of group can has access to view data, edi, delete data of the members enclosed in the same group
 - One person can be Admin of multiple groups but can view data group wise.
 - There should be a Super Admin who can access all the Admins of the groups and users of all groups 
 - Super admin should have all permissions

Users:
 - All users can Create, Edit data in 3 sections
 - user can view data of the other members in the same group but can't edit
 - user from one group can't see data from other groups

 DB:
 There should be a Db in which data can be saved, retrieved, modified
 Prefer any open source Db with minimum size to engage the product
 Create DB schema and suggest columns, tables to present
 Create Roles and permissions for different types of users

UI: 
- Should be responsive to all devices 
- Compatible to all browsers
- Implement (SPA) Single Page Application for the web pages
- UI should be stylish and adhere to modern industry standards
-  UI should be very reative to users.
- Feel of the webpages should be very good and interactive.
- Pick best elements and date calendar and input boxes, icons,Headers, Menu, Tables,  and other elements required to build the webpages
- Login and logout should exist
- only authorised login users can able to access application.
- Data should render as per the roles and persmissions in which user have.

 Technical Details:
 Choose open source frameworks for - coding language, Front end, backend code bases, Db handling, REST Api

Take time and analyse the above criteria. I am open to listen any best suggestions you can give, ask me questions if you are having doubts arises and dont have clarity on something. 