/*
  Copyright (c) 2015 WLDTW2008@gmail.com

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

#include <stdio.h>
#include <stdlib.h>
#include <cassandra.h>
#include <time.h>
#include <stdint.h>
#include <string.h>
#include "common.h"
void vCheckSystex(int argc, char *argv[]) {
	if (argc >= 7)
	{
		//good
	}
	else
	{
		printf("Systex Error\n");
		printf("Systex: %s IP Port dbname dbgflag Symbol FMT\n", argv[0]);
		printf("   FMT: 0=Txt, 1=JSON\n");
		printf("    Ex: %s 127.0.0.1 9042 tqdb1.symbol 1 WTX 0 \n", argv[0]);
		printf("    Ex: %s 127.0.0.1 9042 tqdb1.symbol 0 ALL 1 \n", argv[0]);
		
		exit(0);

	}
}

int main(int argc, char *argv[]) {
	char *pszIP, *pszPort, *pszDBTblName, *pszQSym, *pszQDateBeg, *pszQDateEnd;
        int i, iDBGFlag, iEPIDFilter;
	int iJSON = 0;
	/* Setup and connect to cluster */
	CassFuture* connect_future = NULL;
	CassCluster* cluster = cass_cluster_new();
	CassSession* session = cass_session_new();

	vCheckSystex(argc, argv);
        i = 1;
	pszIP = argv[i++];
	pszPort = argv[i++];
        pszDBTblName = argv[i++];
	iDBGFlag = atoi(argv[i++]);
	pszQSym = argv[i++];
	iJSON = atoi(argv[i++]);
	/*
	if (strcmp(pszQSym,"ALL")==0)
		sprintf(szQStr, "SELECT * from %s", pszDBTblName);
	else
		sprintf(szQStr, "SELECT * from %s where symbol='%s' ", pszDBTblName, pszQSym);
	*/
	cass_cluster_set_port(cluster, atoi(pszPort));
	cass_cluster_set_contact_points(cluster, pszIP);//"192.168.1.217");
	cass_cluster_set_connect_timeout(cluster, 10000);
	cass_cluster_set_request_timeout(cluster, 600000);
	cass_cluster_set_num_threads_io(cluster, 2);
	//cass_cluster_set_protocol_version(cluster, protocol_version);

	connect_future = cass_session_connect(session, cluster);

        std::vector<ST_SymbolInfo> vecSymbolInfo;

	time_t tBeg = time(NULL);
	int iPage = 0;
	int iDataCnt = 0;
	int iFirstLine = 0;
	if (cass_future_error_code(connect_future) == CASS_OK)
	{
		iQAllSymbol(&vecSymbolInfo, "tqdb1", session, cluster);
		if (iJSON)
			printf("[");
		for (i=0;i<(int)vecSymbolInfo.size();++i)
		{
			if (strcmp(pszQSym, "ALL") != 0 && strcmp(pszQSym,vecSymbolInfo[i].symbol.c_str()) != 0)
				continue;

			if (iJSON)
			{
				if (i!=0) printf(",\n");
				printf("{'symbol':'%s','keyval':{", vecSymbolInfo[i].symbol.c_str());
			}
			else
			{
				printf("symbol=%s\n", vecSymbolInfo[i].symbol.c_str());
			}
			while (1)
			{
				int iKeyValCnt = 0;
				std::map<std::string, std::string>::iterator iter;
				for (iter=vecSymbolInfo[i].mapKeyVal.begin( ); iter != vecSymbolInfo[i].mapKeyVal.end( ); ++iter)
				{
					if (iJSON)
					{
						if (iKeyValCnt!=0) printf(",");
						printf("'%s':'%s'", iter->first.c_str(), iter->second.c_str());
					}
					else
					{
						printf("  %s=%s\n", iter->first.c_str(), iter->second.c_str());
					}
					iKeyValCnt++;
				}
				iDataCnt++;
				break;
			}
			if (iJSON)
				printf("}}");
		}
		if (iJSON)
			printf("]\n");
		/* Close the session */
		CassFuture* close_future = cass_session_close(session);
		cass_future_wait(close_future);
		cass_future_free(close_future);

	} else {
		/* Handle error */
                const char* pszMsg;
                size_t iMsgLen;
                cass_future_error_message(connect_future, &pszMsg, &iMsgLen);
		fprintf(stderr, "Unable to connect: '%.*s'\n", iMsgLen, pszMsg);
	}

	cass_future_free(connect_future);
	cass_cluster_free(cluster);
	time_t tEnd = time(NULL);
	if (iDBGFlag)
		printf("total info> page: %d, data cnt: %d, execute time=%d Secs\n", iPage, iDataCnt, tEnd-tBeg);
		
	return 0;
}
