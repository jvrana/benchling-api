# benchlingapi change log
## 2.1.12
**2020-02-12T16:15:11.847504**
changes to Session initialization

 - Users can now specify the home url for the Benchling Session instance. Use Session(api_key, org='myorg') to specify the home url 'myorg.benchling.com/api/v2'. User Session(api_key, home='myorg.benchling.com/api/v2') to specify the home url directly.


## 2.1.11
**2019-12-18T13:34:41.244797**
hotfix sharelink bug




## 2.1.10
**2019-12-17T17:26:29.569759**
fix previous release




## 2.1.9
**2019-12-17T17:16:09.386482**
fixes sharelink bugs




## 2.1.8
**2019-12-17T17:10:53.952392**
re-release of 2.1.7 (fixes broken branch)




## 2.1.7
**2019-12-17T17:07:16.144945**
bug fixes

 - fixes loading DNASequences from share_links


## 2.1.6
**2019-12-16T17:06:05.925041**
bug fixes

 - updates DNASequence to work with latest Benchling API update


## 2.1.5
**2019-12-12T14:18:00.136712**


 - added 'merge' method to entities
 - fixed bug that arose iwhen trying to save an entity containing fields


## 2.1.4
**2019-12-12T14:16:27.446507**
feature and bug fixes




## 2.1.3
**2019-10-23T16:08:47.898865**
fixes bug with DNASequence.archived_reason

 - typo in archive_reason


## 2.1.2
**2019-10-18T13:44:46.826684**
bug fixes

 - fixes bug where parameters in get_pages was not being inherited
 - adds new 'all_in_registry' function


## 2.1.1
**2019-10-17T19:36:37.900149**
Python 3.5, 3.6, 3.7 support




## 2.1
**2019-10-17T12:42:35.238592**
Update marshamllow to 3.2




## 2.0.1
**2019-10-16T08:02:35.118447**
Bug fixes

 - fixed issue where nested data keys were not properly formatted to and from the benchling server


## 2.0.0
**2019-10-15T21:08:34.511953**
Second major release

 - all attribute names now lower-underscore case
 - refactoring and bug fixes
 - updates to interface
 - uses benchling api V2
