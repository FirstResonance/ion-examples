

# Delete all Blank POs Script
# Deletes all POs without Receipts or PO Line Items

from subprocess import call
from getapikey import get_access_token, call_api
import requests
import json
from urllib.parse import urljoin



  # Deletes all Blank POs (must have PO lines and receipts deleted)
DELETEPOSMUTATION='''
    mutation deletePurchaseOrder($id:ID!,$etag:String!)
  {deletePurchaseOrder(id:$id,etag:$etag)
    {
    id
  }
  }
  '''


  # Queries for etags for PO to run mutation to delete them
GETETAGSPOS = '''
  query PurchaseOrders($filterss: PurchaseOrdersInputFilters) {
    purchaseOrders(filters: $filterss) {
      edges {
        node {
          id
          _etag
        }
      }
    }
  }
  '''


access_token = get_access_token()

pos = call_api(GETETAGSPOS,{},access_token)
print(pos)

for po in pos["purchaseOrders"]["edges"]:
   etag=po["node"]["_etag"]
   id=po["node"]["id"]
  call_api(DELETEPOSMUTATION,{"id":id, "etag":etag},access_token)
print("Done!")