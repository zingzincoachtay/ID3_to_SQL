#!/usr/bin/python3
import json,sys,re

def trim(x):
  try: y = x.strip()
  except: y = x
  return y
def errmsg(f,pos):
  x,y = pos
  print( "{}: {}\n\t>>>{}".format(f,x,y) )
def id3v2(flag,query):
  return '{} "{}"'.format(flag, esc2quote(query) )
def esc2quote(str):
  if re.search('"',str) :
    return str.replace('"','\\"')
  else:
    return str
def form_command(mp3,d):
    str = ''
    try:
      album = d['TALB']
      album = id3v2('-A',album)
    except:
      print( 'Error TALB: '+mp3)
      album = ''
    try:
      composer = d['TCOM']
    except:
      composer = 'Zumba Fitness'
    composer = id3v2('--TCOM',composer)
    try:
      genre = d['TCON']
      genre = id3v2('-g',genre)
    except:
      print( 'Error TCON: '+mp3 )
      genre = ''
    try:
      title = d['TIT2']
      title = id3v2('-t',title)
    except:
      print( 'Error TIT2: '+mp3 )
      title = ''
    try:
      artist = d['TPE1']
      artist = id3v2('-a',artist)
    except:
      print( 'Error TPE1: '+mp3 )
      artist = ''
    try:
      cdenum = d['TPOS']
    except:
      cdenum = '1/1'
    cdenum = id3v2('--TPOS',cdenum)
    try:
      track = d['TRCK']
      track = id3v2('-T',track)
    except:
      print( 'Error TRCK: '+mp3 )
      track = ''
    try:
      year = d['TYER']
      year = id3v2('-y',year)
    except:
      year = ''
    print( 'id3v2 -D "{}"'.format(mp3) )
    print( 'id3v2 {} {} {} {} {} {} {} {} "{}"'.format(album,composer,genre,title,artist,cdenum,track,year, mp3 ) )


must = ("TPE1","TALB","TIT2","TCON","TRCK")
#artist
tpe1 = 'Zumba Fitness'
# album name
#talb_1 = 'CD (\d{2})'
#talb_2 = 'ZIN CD (\d{2})'
#talb = 'CDs\/'
talb_cd_1,talb_mm_1 = ['CD (\d{2})','MM (\d{2})']
talb_cd_2,talb_mm_2 = ['ZIN CD (\d{2})','Mega Mix (\d{2})']
talb = 'CDs\/'
#talb_1 = r'MM (\d{2})'
#talb_2 = r'Mega Mix (\d{2})'
#talb = 'MMs\/'
# song title
tit2 = '^.+\/\d{1,2} \- ([^\/]+?) \- .+\s*\.\w{3,4}\s*$'
# genre
tcon = '^.+\/\d{1,2} \- [^\/]+? \- (.+)\s*\.\w{3,4}\s*$'
# track
trck = '^.+\/0*(\d{,2}?) \- [^\/]+? \- [^\/]+\s*\.\w{3,}\s*$'

### recreating the filename and comparing might be simpler
Fcurrent = '^.+\/([^\/]+\.\w{3,})$'

with open(sys.argv[1],encoding='utf8') as tags:
  mp3s = json.load(tags)
  for mp3 in mp3s:
    d = mp3s[mp3]
    # A few exceptions
    try: open(mp3)
    except: errmsg( 'Not found',[mp3,'filename not found'])
    if re.search('B2 CD|GOLD CD 13',mp3) : continue
    #--#--#
    if not all (k in d for k in must) :
      errmsg( 'Error SOME MUST MISSING'
             ,[mp3,'={"TPE1","TALB","TIT2","TCON","TRCK"}'] )
    if all (k not in must for k in d) :
      errmsg( 'Warning new tags found'
             ,[mp3,'only warning; check for the new tags'] )
    if "TPE1" not in d : # Always "Zumba Fitness"
      d.update( {"TPE1":"Zumba Fitness"} )
    if "TALB" not in d : d.update( {"TALB":""} )
    if "TIT2" not in d : d.update( {"TIT2":""} )
    if "TCON" not in d : d.update( {"TCON":""} )
    if "TRCK" not in d : d.update( {"TRCK":""} )
    if "TCOM" not in d : # Always "Zumba Fitness"
      d.update( {"TCOM":"Zumba Fitness"} )
    if "TPOS" not in d : d.update( {"TPOS":"1/1"} )
    #if "TYER" not in d : # only preserve this tag
    #if "TXXX" in d or "COMM" in d : # ignore
    _tpe1 = trim(d["TPE1"])
    _talb = trim(d["TALB"])
    _tit2 = trim(d["TIT2"])
    _tcon = trim(d["TCON"])
    _trck = re.search('^0*(\d{,2})\/\d{,2}$', trim(d["TRCK"]) ).group(1)
    # A few more exceptions
    if _tcon == 'DJ Mix' and re.search('DJ Mix',mp3) : continue
    #--#--#

    # If inconsistencies found, capture and edit JSON.
    if "TPE2" in d and "TPE1" in d :
      errmsg( "Error multiple TPE#"
             ,[mp3,'TPE1 and TPE2 shall not coexist'] ) 
    # Test Artist
    #if _tpe1 != tpe1 : $okay = "if "TPE1" not in d : d.update( {"":""} )
    # Test Album
    y_cd_1 = re.search(talb_cd_1,mp3)
    y_cd_2 = re.search(talb_cd_2,_talb)
    y_mm_1 = re.search(talb_mm_1,mp3)
    y_mm_2 = re.search(talb_mm_2,_talb)
    if not(
         (y_cd_1 and y_cd_2) or (y_mm_1 and y_mm_2)
       ) : 
      # Unmatched, confirm the mimatch
      errmsg( "Error Spelling TALB",[mp3,_talb] )
    elif y_cd_1 and y_cd_2 :
      # ZIN CD Mismatch
      this,that = [y_cd_1.group(1),y_cd_2.group(1)]
      if this != that :
        errmsg( "Error Mismatch TALB",[mp3,_talb] )
    elif y_mm_1 and y_mm_2 :
      # Mega Mix Mismatch
      this,that = [y_mm_1.group(1),y_mm_2.group(1)]
      if this != that :
        errmsg( "Error Mismatch TALB",[mp3,_talb] )
    # Test Title
    try:
      songtitle = re.search(tit2,mp3).group(1)
    except:
      songtitle = ''
      #errmsg( "Error songtitle",[mp3,songtitle] )
    if _tit2 != songtitle :
      # Song Title Mismatch
      errmsg( "Error Spelling TIT2",[mp3,_tit2] )
    try: genre = re.search(tcon,mp3).group(1)
    except:
      genre = ''; #errmsg( "Error genre",[mp3,genre] )
    if _tcon.replace(',',' - ') != genre :
      errmsg( 'Error Mismatch TCON',[mp3,_tcon.replace(',',' - ')] )
    try: tracknum = re.search(trck,mp3).group(1)
    except:
       trcknum = ''; errmsg( "Error track",[mp3,tracknum] )
    if _trck != tracknum : 
      errmsg( 'Error Mismatch TRCK',[mp3,_trck] )
    # Compare filename by filepath and filename by tags
    try: fcurrent = re.search(Fcurrent,mp3).group(1)
    except: 
      fcurrent = ''
      errmsg( "Error NOT FOUND fcurrent"
             ,[mp3,'filename by filepath'] )
    fproposed = '{:02d} - {} - {}.mp3'.format( int(_trck),_tit2,_tcon.replace(',',' - ') )
    if fcurrent != fproposed :
      errmsg( 'Error Mismatch Filenames',[fcurrent,fproposed] )


#    for t in d :
#      print(t)

