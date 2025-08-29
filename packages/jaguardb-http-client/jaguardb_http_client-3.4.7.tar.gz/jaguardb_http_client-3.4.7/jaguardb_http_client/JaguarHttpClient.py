import requests, json
import os.path
from typing import Any, List, Optional, Tuple


################################################################################
##
##  Make sure you have a jaguar fwww http server running
##
################################################################################

import os, json

class JaguarHttpClient():

    ''' ctor, takes a http REST endpoint
        url is like "http://192.168.5.100:8080/fwww/"
        url is like "fakeurl"
    '''
    def __init__(self, url):
        if url[-1] != '/':
            url = url + '/'
        self.url = url


    ''' First step is to login and get an auth token
    returns valid token for success or None for failure.
    Users can pass in 'demouser' for apikey for demo purpose.
    '''
    def login(self, apikey=None):
        if self.url == 'fakeurl/':
            return 'faketoken'

        self.apikey = apikey
        self.token = ''

        if apikey is None:
            self.apikey = self.getApikey()

        params = { "req": "login", "apikey": apikey }
        response = requests.get(self.url, params=params)
        #print(f"in login() apikey={apikey}  response ={response}")
        if response.status_code == 200:
            json_data = json.loads(response.text)
            token = json_data['access_token']
            if token is not None:
                self.token = token
                return token
            else:
                return None
        else:
            return None

    ''' makes GET call and returns response
    GET is faster than POST, but request size is limited
    '''
    def get(self, qs, token):
        bearerToken = 'Bearer ' + token
        headers = { "Authorization": bearerToken }
        params = { "req": qs, "token": token }
        response = requests.get(self.url, headers = headers, params = params )
        return response

    ''' makes a POST request and returns response
    '''
    def post(self, qs, token, withfile=False):
        bearerToken = 'Bearer ' + token
        headers = { "Authorization": bearerToken }

        if withfile is True:
            params = { "req": qs, "token": token, "withfile": "yes" }
        else:
            params = { "req": qs, "token": token }

        response = requests.post(self.url, headers = headers, json = params )
        return response

    ### alias for post() since query() normally has large size involving vectors
    def query(self, qs, token, withfile=False):
        return self.post( qs, token, withfile )


    ''' logout is strongly recommended for security reasons
    and resource cleanup
    '''
    def logout(self, token):
        bearerToken = 'Bearer ' + token
        headers = { "Authorization": bearerToken }
        params = { "request": "logout", "token": token }
        requests.get(self.url, headers = headers, params = params )

    ### wrapper
    def getApiKey(self):
        return self.getApikey()


    ''' If apikey is not provided, this tries to get it from $HOME/.jagrc file
    '''
    def getApikey(self):
        try:
            hm = os.getenv("HOME")
            fpath = hm + "/.jagrc"
            f = open(fpath, 'r')
            key = f.read()
            key = key.strip()
            f.close()
            return key
        except Exception as e:
            return ''

    ''' get json from server and parse out the data element
    '''
    def jsonData(self ):
        try:
            j = self.jag.json()
            data = json.loads(j)
            return data['data']
        except Exception as e:
            return ''

    ''' given json string from server, get the data element
    '''
    def getData(self, j):
        try:
            data = json.loads(j)
            return data['data']
        except Exception as e:
            return ''


    ''' post a file to url server index=[1...pos] index is position of the file field
    inside values ('0','1','2','3') in insert statement. Index starts from 1 when invoked. 
    Call this to upload the files, before the insert query
    '''
    def postFile(self, token, filePath, index ):
        try:
            filefp = open(filePath, 'rb');
            if filefp is None:
                return False
        
            ## starts from 0 now
            index = index - 1
            name = 'file_' + str(index)
            files = {name: (filePath, filefp) }
            params = { "token": token }
            bearerToken = 'Bearer ' + token
            headers = { "Authorization": bearerToken }
            response = requests.post(self.url, headers=headers, data=params, files=files)
            filefp.close()
            if response.status_code == 200:
                return True
            return False
        except Exception as e:
            return False 
    
    '''
    get URL for display of files in a browser
    '''
    def getFileUrl(self, token, pod, store, column, zid):
        podstore = pod + '.' + store
        bearerToken = 'Bearer ' + token
        headers = { "Authorization": bearerToken }
        query = "getfile " + column + " show from " + podstore + " where zid='" + zid + "'"
        params = { "req": query, "token": token };
        response = requests.get(self.url, headers=headers, params = params)
        if response.status_code == 200:
            js = json.loads(response.text)
            return self.url + "?" + js[0]
        else:
            return ''
    

    '''
    drop a store 
    '''
    def dropStore(self, pod, store):
        podstore = pod + '.' + store

        qs = "drop store " + podstore
        resp = self.post(qs, self.token)
        if resp.status_code == 200:
            return True
        return False

    '''
    create a store 
    '''
    def createStore(self, schema):

        pod, store, columns = self._parseSchema(schema)
        podstore = pod + '.' + store

        qs = "create store " + podstore + "(" + columns + ")"
        #print(f"createStore qs={qs}")

        resp = self.post(qs, self.token)
        if resp.status_code == 200:
            return True
        return False

    '''
    add data collection to store
    '''
    def add(self, pod, store, files, tensors, scalars ):
        """
        write data to store
        Args:
            files: [{"filepath": "/tmp/a/b/a.jpg", "position": 1}, {"filepath": "/tmp/a/b/b.jpg", "position": 4}]
                    filepath is full file path, 1 and 4 are column positions of the file columns.
                    You can attach multiple files in a collection.

            tensors: list of embeddings for all vector columns [[....], [....]]
            scalars: list of values for non-vector columns
        Returns:
            {} for invalid token, or
            json result string
        """

        podstore = pod + '.' + store

        withFile = False
        for filedict in files:
            fpath = filedict['filepath']
            position = filedict['position']
            rc = self.postFile(self.token, fpath, position )
            #print(f"postFile {fpath} rc={rc}")
            withFile = True

        data_list = []
        for vec in tensors:
            s = ",".join([str(e) for e in vec])
            data_list.append( "'" + s + "'")

        for s in scalars:
            data_list.append( "'" + s + "'")

        ins = ",".join(data_list)

        #print(f"add ins={ins}")

        qs = "insert into " + podstore + " values (" + ins + ")"
        #print(f"insert stmt qs={qs}")

        resp = self.post(qs, self.token, withFile)
        #print(f"post resp={resp}")
        #print(f"resp.text={resp.text}")

        if resp.status_code != 200:
            return ''

        jd = json.loads(resp.text)
        return jd['zid']

    '''
    run command
    '''
    def run(self, query: str, withFile: bool = False):
        """
        Run any query statement in jaguardb
        Args:
            query (str): query statement to jaguardb
        Returns:
            {} for invalid token, or
            json result string
        """
        if self.token == "":
            return {}

        resp = self.post(query, self.token, withFile)
        txt = resp.text
        try:
            js = json.loads(txt)
            return js
        except Exception:
            return {}

    '''
     count number of collections in a store
    '''
    def count(self, pod, store):
        """
        Count records of a store in jaguardb
        Args: no args
        Returns: (int) number of records in pod store
        """
        podstore = pod + "." + store
        q = "select count() from " + podstore
        js = self.run(q)
        if isinstance(js, list) and len(js) == 0:
            return 0
        jd = json.loads(js[0])
        return int(jd["data"])

    '''
    delete collectons in a store by zids
    '''
    def delete(self, pod, store, zids):
        """
        Delete records in jaguardb by a list of zero-ids
        Args:
            pod (str):  name of a Pod
            ids (List[str]):  a list of zid as string
        Returns:
            Do not return anything
        """
        podstore = pod + "." + store
        for zid in zids:
            q = "delete from " + podstore + " where zid='" + zid + "'"
            self.run(q)

    '''
    clear out (remove) collections in a store
    Leave schema untouched
    '''
    def clear(self, pod, store):
        """
        Delete all records in jaguardb
        Args: No args
        Returns: None
        """
        podstore = pod + "." + store
        q = "truncate store " + podstore
        self.run(q)

    def is_anomalous( self, pod, store, vector_index, vector_type, embeddings):
        """
        Detect if given embedding is anomalous from the dataset
        Args:
            pod
            store
            vector_index  :  name of vector column
            vector_type: type of vector index  (cosine_fraction_float etc)
            embeddings: list of embeddings
        Returns:
            True or False
        """
        vcol = vector_index  #  name of vector column
        vtype = vector_type  #  cosine_fraction_float

        qv_comma = ",".join(embeddings)
        podstore = pod + "." + store
        q = "select anomalous(" + vcol + ", '" + qv_comma + "', 'type=" + vtype + "')"
        q += " from " + podstore

        js = self.run(q)
        if isinstance(js, list) and len(js) == 0:
            return False
        jd = json.loads(js[0])
        if jd["anomalous"] == "YES":
            return True
        return False


    '''
    perform similarity search
    '''
    def similarity_search_with_score(
        self, pod, store,
        vector_index, vector_type,
        embeddings,
        k: int = 3,
        fetch_k: int = -1,
        where: Optional[str] = None,
        args: Optional[str] = None,
        metadatas: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Tuple[str, dict, float]]:
        """
        Return Jaguar documents most similar to query, along with scores.
        Args:
            query: Text to look up documents similar to.
            k: Number of Documents to return. Defaults to 3.
            lambda_val: lexical match parameter for hybrid search.
            where: the where clause in select similarity. For example a
                where can be "rating > 3.0 and (state = 'NV' or state = 'CA')"
            args: extra options passed to select similarity
            kwargs:  vector_index=vcol, vector_type=cosine_fraction_float
        Returns:
            List of elements most similar to the query embeddings and score for each.
            List of Tuples of (text, metadata, similarity_score)
        """
        vcol = vector_index
        vtype = vector_type
        str_embeddings = [str(f) for f in embeddings]
        qv_comma = ",".join(str_embeddings)
        podstore = pod + "." + store
        q = (
            "select similarity("
            + vcol
            + ",'"
            + qv_comma
            + "','topk="
            + str(k)
            + ",fetch_k="
            + str(fetch_k)
            + ",type="
            + vtype
        )
        q += ",with_score=yes,with_text=yes"
        if args is not None:
            q += "," + args

        if metadatas is not None:
            meta = "&".join(metadatas)
            q += ",metadata=" + meta

        q += "') from " + podstore

        if where is not None:
            q += " where " + where

        jarr = self.run(q)
        if jarr is None:
            return []

        docs_with_score = []
        for js in jarr:
            score = js["score"]
            text = js["text"]
            zid = js["zid"]

            ### give metadatas
            md = {}
            md["zid"] = zid
            if metadatas is not None:
                for m in metadatas:
                    mv = js[m]
                    md[m] = mv

            tup = (text, md, score)
            docs_with_score.append(tup)

        return docs_with_score


    def search(
        self, pod: str, store:str, vector_index:str, vector_type:str,
        embeddings: List[float],
        topk: int = 3,
        where: Optional[str] = None,
        metadatas: Optional[List[str]] = None,
        **kwargs: Any,
    ):
        """
        Return Jaguar documents most similar to query, along with scores.
        Args:
            query: Text to look up documents similar to.
            k: Number of Documents to return. Defaults to 5.
            where: the where clause in select similarity. For example a
                where can be "rating > 3.0 and (state = 'NV' or state = 'CA')"
        Returns:
            List of Documents most similar to the query
        """
        docs_and_scores = self.similarity_search_with_score(pod, store, vector_index, vector_type,
            embeddings, topk=topk, where=where, metadatas=metadatas, **kwargs
        )
        return docs_and_scores


    '''
    parse schema into string containing separate columns
    schema:
      schema = {
        "pod": "mypod",
        "store": "mystore",
        "columns": [
            {"name": "vec", "type": "vector", "dim":"512", "dist":"euclidean", "input":"fraction", "quantization":"float"},
            {"name": "path", "type": "str", "size": "64"},
            {"name": "tms", "type": "datetime" },
            {"name": "seq", "type": "bigint" },
            {"name": "num", "type": "int" },
        ]
      } 

    For vector column:
        dist is distance type, valid types are: cosine euclidean innerproduct manhatten hamming chebyshev minkowskihalf jeccard
        input is input data type, valid types are: fraction whole
        quantization is storage quantization type, valid types are: float short byte
    '''
    def _parseSchema(self, schema):
        pod = schema['pod']
        store = schema['store']
        columns = schema['columns']
        cols = [] 

        ### add vector columns first
        for col in columns:
            name = col['name']
            tp = col['type']
            if tp == 'vector':
                dim = col['dim'] 
                dist = col['dist'] 
                if self._validDistanceType(dist) is False:
                    return '', '', ''

                input_type = col['input'] 
                if self._validInputType(input_type) is False:
                    return '', '', ''

                quantization = col['quantization'] 
                if self._validQuantizationType(quantization) is False:
                    return ''

                vtype = dist + '_' + input_type + '_' + quantization
                c = name + ' vector(' + dim + ", '" + vtype + "')" 
                cols.append(c)
            else:
                continue
                

        ### add other columns
        for col in columns:
            name = col['name']
            tp = col['type']
            if tp == 'str':
                size = col['size'] 
                c = name + ' char(' + size + ')'
            elif tp == 'vector':
                continue
            else:
                c = name + ' ' + tp
                
            cols.append(c)

        cs = ",".join(cols)
        return pod, store, cs

    '''
    validate distance type
    '''
    def _validDistanceType(self, dist):
        if dist == 'cosine':
            return True
        if dist == 'euclidean':
            return True
        if dist == 'innerproduct':
            return True
        if dist == 'manhatten':
            return True
        if dist == 'hamming':
            return True
        if dist == 'chebyshev':
            return True
        if dist == 'minkowskihalf':
            return True
        if dist == 'jeccard':
            return True

        return False

    '''
    validate data input type
    input_type: fraction [-1,1]
    input_type: whole can be any number, not limited to fractional numbers
    '''
    def _validInputType(self, input_type):
        if input_type == 'fraction':
            return True
        if input_type == 'whole':
            return True

        return False

    '''
    validate storage quantization type
    float uses 4 bytes, short uses 2 bytes, byte uses 1 byte
    '''
    def _validQuantizationType(self, quant_type):
        if quant_type == 'float':
            return True
        if quant_type == 'short':
            return True
        if quant_type == 'byte':
            return True

        return False

    '''
    get file from files for the colidx
    '''
    def _pickFileName(self, files, colidx):
        for filedict in files:
            fpath = filedict['filepath']
            position = filedict['position']
            if colidx == position:
                return fpath
        return ''

### example test program
if __name__ == "__main__":
    
    url = "http://192.168.1.88:8080/fwww/"
    jag = JaguarHttpClient( url )
    #apikey = 'my_api_key'
    apikey = jag.getApikey()
    apikey = 'demouser'


    ### login to get an authenticated session token
    token = jag.login(apikey)
    print(f"got token {token}")
    if token == '':
        print("Error login")
        exit(1)
    print(f"session token is {token}")

    ### get some data
    resp = jag.get("help", token)
    print(resp.text)

    j1 = json.loads(resp.text)
    helpjson = j1[0]
    j2 = json.loads(helpjson)
    print(j2['data'])


    q = "drop store vdb.week"
    response = jag.get(q, token)
    print(response.text)
    print(f"drop store {response.text}")

    q = "create store vdb.week ( v vector(512, 'euclidean_fraction_float'), v:f file, v:t char(1024), a int)"
    response = jag.get(q, token)
    print(f"create store {response.text}", flush=True)


    imgfile1 = '../test/test1.jpg';
    if not os.path.isfile(imgfile1):
        print(f"imgfile {imgfile1} does not exist, you must create it first")
        exit(1)

    imgfile2 = '../test/test2.jpg';
    if not os.path.isfile(imgfile2):
        print(f"imgfile {imgfile2} does not exist, you must create it first")
        exit(1)

    imgfile3 = '../test/test3.jpg';
    if not os.path.isfile(imgfile3):
        print(f"imgfile {imgfile3} does not exist, you must create it first")
        exit(1)


    ### upload file for v:f which is at position 2 
    rc = jag.postFile(token, imgfile1, 2 )
    print(f"postFile {imgfile1} {rc}")

    q = f"insert into vdb.week values ('0.1,0.2,0.3,0.4,0.5,0.02,0.3,0.5', '{imgfile1}', 'this is text description: windy ', 10 )"
    response = jag.post(q, token, True)
    print(f"insert response.text {response.text}")
    jd = json.loads(response.text)
    print(f"insert zid = {jd['zid']}")

    q = f"insert into vdb.week values ('0.5,0.2,0.5,0.4,0.1,0.02,0.3,0.7', '{imgfile2}', 'this is text description: sunny', 100 )"
    response = jag.post(q, token, True)
    print(f"insert response.text {response.text}", flush=True)
    jd = json.loads(response.text)
    print(f"insert zid = {jd['zid']}")

    q = "select similarity(v, '0.3,0.2,0.8,0.4,0.1,0.1,0.3,0.1', 'topk=3, type=euclidean_fraction_float, with_text=yes, with_score=yes') from vdb.week"
    response = jag.post(q, token)
    print(f"t100 select sim:  res={response}")
    print(f"t101 select sim:  res.text={response.text}")
    jarr = json.loads(response.text)
    print(f"select sim jarr={jarr}", flush=True)

    for obj in jarr:
        zid = obj['zid']
        field = obj['field']
        vid = obj['vectorid']
        dist = obj['distance']
        txt = obj['text']
        score = obj['score']
        print(f"field=[{field}]  vectorid=[{vid}]  distance=[{dist}] text=[{txt}] score=[{score}]", flush=True)

        furl = jag.getFileUrl(token, "vdb", "week", "v:f", zid)
        print(f"file url={furl}", flush=True)

    
    ########################### new API 3/3/2024 ######################################################################
    ### create, add, select with new API
    schema = {
        "pod": "vdb",
        "store": "mystoreapi",
        "columns": [
            {"name": "vec", "type": "vector", "dim":"3", "dist":"euclidean", "input":"fraction", "quantization":"float"},
            {"name": "vec:text", "type": "str", "size": "1024"},
            {"name": "vec:img1", "type": "file" },
            {"name": "vec:img2", "type": "file" },
            {"name": "path", "type": "str", "size": "64"},
            {"name": "tms", "type": "datetimesec" },
            {"name": "seq", "type": "bigint" },
            {"name": "num", "type": "int" },
        ]
    } 

    rc = jag.dropStore("vdb", "mystoreapi")
    print(f"dropStore rc={rc}")

    rc = jag.createStore(schema)
    print(f"createStore rc={rc}")

    ### insert one collection
    files = [{"filepath": "../test/test1.jpg", "position": 3}, {"filepath": "../test/test2.jpg", "position": 4}]
    tensors = [['0.2', '0.3', '0.51']]
    scalars = ['first product description', '../test/test1.jpg', '../test/test2.jpg', '/path/123/d1', '2024-02-09 11:21:32', '1001', '8']
    zid = jag.add("vdb", "mystoreapi", files, tensors, scalars )
    print(f"insert zid={zid}")

    ### insert another collection
    files = [{"filepath": "../test/test3.jpg", "position": 3}, {"filepath": "../test/test4.jpg", "position": 4}]
    tensors = [['0.1', '0.5', '0.71']]
    scalars = ['second product description ', '../test/test3.jpg', '../test/test4.jpg', '/path/234/d2', '2024-02-12 15:21:32', '1002', '9']
    zid = jag.add("vdb", "mystoreapi", files, tensors, scalars )
    print(f"add zid={zid}")


    embeddings = ['0.2', '0.4', '0.31']
    docs = jag.search( "vdb", "mystoreapi", "vec", "euclidean_fraction_float", embeddings, topk=3 )
    print(f"search1 docs={docs}")


    where = "num='8'"
    docs = jag.search( "vdb", "mystoreapi", "vec", "euclidean_fraction_float", embeddings, topk=3, where=where )
    print(f"search2 docs={docs}")

    ### initial search base is fetch_k=100 then narrows down to topk=3
    where = "num='9'"
    metadatas = ['seq', 'num', 'tms']
    docs = jag.search( "vdb", "mystoreapi", "vec", "euclidean_fraction_float", embeddings, 
                       fetch_k=100, topk=3, where=where, metadatas=metadatas )
    print(f"search3 docs={docs}")

    jag.logout(token)
