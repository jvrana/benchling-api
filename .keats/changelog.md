# benchlingapi change log
## 2.1.4
**2019-11-15T18:23:57.647864**
New features: DNAAlignment and Task as new models

 - Added the `DNAAlignment` class to represent alignments
 - Added the `Task` class to represent long running tasks. `task.wait()` waits for server task to finish. `task.response_class` returns the expected model, if there is one.


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
