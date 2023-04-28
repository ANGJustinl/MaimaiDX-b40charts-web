import httpx

 
async def get(url):
    async with httpx.AsyncClient(verify=False, timeout=None) as client:
      resp = await client.get(
        url,    
      )
      return resp

      