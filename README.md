# gracies-eats-backend
Lambda codebase for performing CRUD operations on Gracie's Eats DynamoDB table. Uses AWS SAM to provision resources for quick and easy deployment. 

To build for deployment or local testing with sam, run:
```
pipenv requirements > src/requirements.txt
sam build
```

SAM needs the requirements.txt file to be inside of the src folder (or whichever folder you specify in template.yaml for the CodeURI field)