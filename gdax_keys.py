

def GetAPIKeys(fname):
  """
  Reads API access info from the specified file and returns the
  key, secret and passphrase.
  """
  with open(fname) as f:
    content = f.readlines()
  # you may also want to remove whitespace characters like `\n` at the end of each line
  content = [x.strip() for x in content] 
  if (len(content) != 3):
    raise Exception("Error: file includes more than 3 lines")
  
  #return key, secret, passphrase
  return (content[0], content[1], content[2])
