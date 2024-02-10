# Location Search Application

This application allows users to search for locations based on various parameters such as place name, postal code, state, and more. The application utilizes four datasets to provide comprehensive location information: IN.txt (removed from dataset due to large size), IN-pincode.txt, states.txt, and feature_code.txt. Details of the data transformation process are documented in the attached IPython notebook.

## Getting Started

 To start the application, follow these steps:
- Build and start the application: 
- Run the following command to build and start the application:
- Unzip documents folder to use it to add the doucuments to ES
```sh
docker-compose up --build
```


 - Create indexes and add data: After the build process is complete, execute four POST requests to create indexes and add data:

- Send the first POST request to `` localhost:5001/create_index`` with the following JSON body:
``
{
  "index_name": "pincode_data"
}
``

- Send the second POST request to ``localhost:5001/create_index`` with the following JSON body:
``
{
  "index_name": "location_data"
}
``

- Then, send two POST requests to ``localhost:5001/add_data`` to add data to the indexes:

- For the first request, use the following JSON body:
``
{
  "index_name": "pincode_data"
}
``
- For the second request, use the following JSON body:
``
{
  "index_name": "location_data"
}
``

 Note: Adding data might take some time due to the large number of records. Please be patient.

 Access the application: Once the data has been added successfully, you can access the application in your browser at ``localhost:5001`` and query the results. 

 # Ensure that the index_name parameter and it's value is set as mentioned above.
