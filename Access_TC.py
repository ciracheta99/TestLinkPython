
import sys, os.path
import datetime
import xmlrpc.client
from subprocess import Popen, PIPE

SERVER_URL = "http://127.0.0.1:81/testlink/lib/api/xmlrpc/v1/xmlrpc.php"
DEVKEY = "1f12ff2818f0f044a944db95ef660207"
testscript = "TestScriptName"
testscriptrevision = "TestScriptRevision"
testdata = "TestDataFile"



class TestLinkDataExtraction:
    def __init__(self, testprojectName, testplanName, devKey=DEVKEY, url=SERVER_URL):
        self.url = url
        self.server = xmlrpc.client.ServerProxy(self.url)
        self.devKey = devKey
        self.testprojectName = testprojectName
        self.testplanName = testplanName
        self.testscript = testscript
        self.testscriptrevision = testscriptrevision
        self.testdata = testdata
        
    def gettestdatastructure(self):
        projectID = self._getTestprojectID_()
        testcaseID = self._getTestcaseID_()
        testdataStructure = {}
        testplanID = self._getTestplanID_()
        for testkey in testcaseID:
            customfieldArray = []
            customfieldArray.append(testplanID)
            testcaseexternalid = projectID[1]+'-'+testcaseID[testkey][0]['external_id']
            version = int(testcaseID[testkey][0]['version'])
            testprojectid = projectID[0]
            send = {'devKey': self.devKey, 'testcaseexternalid': testcaseexternalid, 'version': version, 'testprojectid': testprojectid, 'customfieldname': self.testscript}
            response = self.server.tl.getTestCaseCustomFieldDesignValue(send)
            customfieldArray.append(response)
            send = {'devKey': self.devKey, 'testcaseexternalid': testcaseexternalid, 'version': version, 'testprojectid': testprojectid, 'customfieldname': self.testdata}
            response = self.server.tl.getTestCaseCustomFieldDesignValue(send)
            customfieldArray.append(response)
            send = {'devKey': self.devKey, 'testcaseexternalid': testcaseexternalid, 'version': version, 'testprojectid': testprojectid, 'customfieldname': self.testscriptrevision}
            response = self.server.tl.getTestCaseCustomFieldDesignValue(send)
            customfieldArray.append(response)
            customfieldArray.append(testcaseID[testkey][0]['tcase_name'])
            testdataStructure[testkey] = customfieldArray
        return [testdataStructure, testplanID]
    
    def getInfo(self):
        return self.server.tl.about()
    
    def getProjects(self):
        return self.server.tl.getProjects(dict(devKey=self.devKey))
    
    def _getTestplanID_(self):
        send = {"devKey": self.devKey, "testprojectname": self.testprojectName, "testplanname": self.testplanName}
        response = self.server.tl.getTestPlanByName(send)
        return response[0]['id']
    
    def _getTestprojectID_(self):
        send = {"devKey": self.devKey, "testprojectname": self.testprojectName}
        response = self.server.tl.getTestProjectByName(send)
        return [response['id'], response['prefix']]
    
    def _getTestcaseID_(self):
        send = {"devKey": self.devKey, "testplanid": self._getTestplanID_()}
        response = self.server.tl.getTestCasesForTestPlan(send)
        return response
    


    
class ExecuteTestPlan():
    def __init__(self, datastruct, testplanid, devKey=DEVKEY, url=SERVER_URL):
        
        self.url = url
        self.server = xmlrpc.client.ServerProxy(self.url)
        self.devKey = devKey
        self.datastruct = datastruct
        self.logfilename = 'NONE'
        self.log = 'NONE'
        self.testplanid = testplanid
        self.testcaseid = 'NONE'
        self.buildname = 'NONE'
        
    def createBuild(self, testplanid, buildname):
        send = {"devKey": self.devKey, "testplanid": self.testplanid, "buildname": buildname}
        self.server.tl.createBuild(send)
       
    
    def logResult(self, string):
        timestamp = datetime.datetime.now()
        stringtoprint = '[' + str(timestamp) + '] ' + str(string) + '\n'
        self.log.write(stringtoprint)
        
    def reportTCResults(self, status):
        data = {"devKey":self.devKey, "testcaseid":self.testcaseid, "testplanid":self.testplanid, "buildname": self.buildname, "status":status}
        return self.server.tl.reportTCResult(data)
    
    def runScript(self):
        timestamp = datetime.datetime.now()
        self.buildname = 'Build-' + str(timestamp)
        self.createBuild(self.testplanid, self.buildname)
        for keys in self.datastruct:
            self.testcaseid = keys
            self.logfilename = self.datastruct[keys][4]+".log"
            self.log = open(self.logfilename, "w+")
            self.log.close()
            self.log = open(self.logfilename, "a+")
            testscriptname = self.datastruct[keys][1]
            try:
                script = open(testscriptname, 'r')
                toeval = script.read()
                exec(toeval)
            except:
                print("Some problem with script execution", testscriptname)
            self.log.close()

        def sendCommand(self, sendcommand):
            firecommand = Popen(str(sendcommand), shell = True, stdout = PIPE, stderr = PIPE)
            stdout, stderr = firecommand.communicate()
            if(stdout):
                return stdout
            elif(stderr):
                print ('Error in output of command')
                return stderr






instance = TestLinkDataExtraction("Evaluation_101", "TestPlan1")
back = instance.gettestdatastructure()
print(back)
execute = ExecuteTestPlan(back[0], back[1])
execute.runScript()

instance = TestLinkDataExtraction("Evaluation_101", "TestPlan2")
back = instance.gettestdatastructure()
print(back)
execute = ExecuteTestPlan(back[0], back[1])
execute.runScript()