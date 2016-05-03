from safebrowsinglookup import SafebrowsinglookupClient
import sys


def getDomainStatus(domain):
	
	#key is linked to my Gmail account and will limit to
	# 10,000 lookups per day. 
	api_key = 'ABQIAAAA_ZP3Gp39cTLiKArCd3K0GhQs0x-2rr_UO6hjtMF0uHW-GkhMSA'
	gsb = SafebrowsinglookupClient(api_key, 0, 0)
	return gsb.lookup(domain)

if __name__ == '__main__':
    response = getDomainStatus(sys.argv[1])
    print response
