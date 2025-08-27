import pytse_client as tse

#pytse_client 0.11.0

def get(sahm):
  ticker = tse.Ticker(sahm)
  return(ticker)   


