

# Delete all POs Script
# Deletes all Receipts (ones assoc. with PO Lines can't be deleted)
# Deletes all PO lines (ones assoc. with POs can't be deleted)
# Deletes all POs

from subprocess import call
from getapikey import get_access_token, call_api
import requests
import json
from urllib.parse import urljoin
def main():
  
  API_URL = 'https://api.buildwithion.com'
  AUTHENTICATION_SERVER = 'auth.buildwithion.com'

  # Deletes all POs (must have PO lines deleted)
  DELETEPOSMUTATION='''
    mutation deletePurchaseOrder($id:ID!,$etag:String!)
  {deletePurchaseOrder(id:$id,etag:$etag)
    {
    id
  }
  }
  '''
  GETRECEIPTS='''
  query receipts($filters:ReceiptsInputFilters)
  {
  receipts(filters:$filters) {
    edges {
      node {
        id
        _etag
      }
    }
  }

  }

  '''
  DELETERECEIPTS='''
  mutation deleteReceipt($id:ID!,$etag:String!)
  {
      deleteReceipt(id:$id,etag:$etag)
      {
          id
      }
  }
  '''

  # deletes all PO lines (must have receips deleted)
  DELETEMUTATION = '''
      mutation deletePurchaseOrderLine($id:ID!,$etag:String!)
  {deletePurchaseOrderLine(id:$id,etag:$etag)
    {
    id 
  }
  }
  '''
  # Queries for etags for PO line to run mutation to delete them 
  GETETAGS = ''' 
  query PurchaseOrderLines($filterss: PurchaseOrderLinesInputFilters) {
    purchaseOrderLines(filters: $filterss) {
      edges {
        node {
          id
          _etag
        }
      }
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
  # Query Variables getting the PO line information based on PO ID

  access_token = get_access_token()


  recs = call_api(GETRECEIPTS,{},access_token)
  polines = call_api(GETETAGS,{},access_token)
  for rec in recs["receipts"]["edges"]:
      etag=rec["node"]["_etag"]
      id=rec["node"]["id"]
      call_api(DELETERECEIPTS,{"id":id,"etag":etag},access_token)

  for poline in polines["purchaseOrderLines"]["edges"]:
      etag=poline["node"]["_etag"]
      id=poline["node"]["id"]
      call_api(DELETEMUTATION,{"id":id, "etag":etag},access_token)

  pos = call_api(GETETAGSPOS,{},access_token)

  for po in pos["purchaseOrders"]["edges"]:
      print(po)
      etag=po["node"]["_etag"]
      id=po["node"]["id"]
      call_api(DELETEPOSMUTATION,{"id":id, "etag":etag},access_token)
if __name__ == "__main__":
  main()
