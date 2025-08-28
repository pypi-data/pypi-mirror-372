from time import sleep
import asyncio

class RequestManager():
    def __init__(self) -> None:
        self.results = {}

        self.req_id = 9999
    
    def set(self, tag, req_id, result):
        if not self.results.get(tag):
            self.results[tag] = {}
        self.results[tag][req_id] = result

    def get(self, tag, req_id):
        if not self.results.get(tag):
            return None

        result = self.results.get(tag).get(req_id)
        if not result:
            return None
        
        del(self.results.get(tag)[req_id])
        return result

    # async def loop_get(self, tag, req_id):
    #     while True:
    #         # breakpoint()
    #         print('self.results.get(tag)==>', self.results.get(tag))
    #         if self.results.get(tag):
    #             result = self.results.get(tag).get(req_id)
    #             if result:
    #                 del(self.results.get(tag)[req_id])
    #                 return result
    #         asyncio.sleep(1)
    
    def next_id(self):
        self.req_id += 1
        return self.req_id
    
class Tags:
    CONTRACT_DETAILS = 'CONTRACT_DETAILS'