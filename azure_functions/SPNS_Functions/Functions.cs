using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json.Linq;
using Microsoft.WindowsAzure.Storage.Table;
using Microsoft.WindowsAzure.Storage;
using System.Threading.Tasks;
using System;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Azure.WebJobs.Extensions.SignalRService;
using Azure;
using System.Collections.Concurrent;
using System.ComponentModel;
using static System.Collections.Specialized.BitVector32;
using System.Drawing;
using System.Linq;
using System.Collections.Generic;

namespace SPNS_Functions
{
    public static class Functions
    {
        const String DefaultUrl = "https://spnswebapp.azurewebsites.net/";

        /* 
         * Function InsertVehicleEntity: inserts a new vehicle captured in an entrance to the parking lot 
         */
        [FunctionName("InsertVehicleEntity")]
        public async static Task<IActionResult> InsertVehicleEntity(
            [HttpTrigger(AuthorizationLevel.Anonymous, "get", "post", Route = "InsertVehicleEntity")] HttpRequest req, 
            ILogger log)
        {
            var entity = new VehicleEntity
            {
                PartitionKey = "0",
                RowKey = req.Form["LicensePlate"],
                LicensePlate = req.Form["LicensePlate"],
                Section = req.Form["Section"],
                Floor = Int32.Parse(req.Form["Floor"]),
                Timestamp = DateTime.UtcNow
            };
            
            // Retrieve the storage account connection string from the app settings, parse and create a reference to the table
            string storageConnectionString = Environment.GetEnvironmentVariable("AzureWebJobsStorage");
            CloudStorageAccount storageAccount = CloudStorageAccount.Parse(storageConnectionString);
            CloudTableClient tableClient = storageAccount.CreateCloudTableClient();
            CloudTable table = tableClient.GetTableReference("ParkingSectionsOccupancy");

            // Create the insert operation
            var insertOperation = TableOperation.Insert(entity);
            await table.ExecuteAsync(insertOperation);

            // TODO: Create a unique URL for this car with Azure Web App services. The URL will also show on the IOT device screen.
            // the URL will look like so: DefaultUrl + entity.LicensePlate.need to implement URL redirection in Azure
            // String uniqeUrl = DefaultUrl + entity.LicensePlate;

            String ResultMessage = $"Vehicle entity inserted successfully. License Plate: {entity.LicensePlate}, Section: {entity.Section}, Floor: {entity.Floor}";
            return new OkObjectResult(ResultMessage);
        }

        /* 
         * Function RemoveVehicleEntity: Removes a vehicle from the parking lot occupancy table 
         * 1. update user map location
         * 2. delete license plate from Azure table
         */
        [FunctionName("RemoveVehicleEntity")]
        public async static Task<IActionResult> RemoveVehicleEntity(
            [HttpTrigger(AuthorizationLevel.Anonymous, "get", "post", Route = "RemoveVehicleEntity")] HttpRequest req,
            [SignalR(HubName = "ParkingChat")] IAsyncCollector<SignalRMessage> signalRMessages,
            ILogger log)
        {
            // Retrieve the storage account connection string from the app settings, parse and create a reference to the table
            string storageConnectionString = Environment.GetEnvironmentVariable("AzureWebJobsStorage");
            CloudStorageAccount storageAccount = CloudStorageAccount.Parse(storageConnectionString);
            CloudTableClient tableClient = storageAccount.CreateCloudTableClient();
            CloudTable table = tableClient.GetTableReference("ParkingSectionsOccupancy");

            // Get the license plate from the request
            log.LogInformation("taking req info");
            string LicensePlate = req.Form["LicensePlate"];
            string Section = req.Form["Section"];
            int Floor = Int32.Parse(req.Form["Floor"]);

            // 1.
            // Update the user's map using Azure SignalR
            string mapUpdateValue = $"F{Floor}_{Section}";
            await signalRMessages.AddAsync(new SignalRMessage
            {
                // UserId = LicensePlate, // Or replace with the appropriate user ID
                Target = "UpdateMap",
                Arguments = new object[] { mapUpdateValue }
            });

            log.LogInformation("SignalR message sent to update map for License Plate: {LicensePlate}", LicensePlate);

            // 2.
            // Query the database and remove all entries of that vehicle
            String ResultMessage = $"Vehicle entity removed successfully.";
            TableQuery<VehicleEntity> query = new TableQuery<VehicleEntity>().Where(TableQuery.GenerateFilterCondition("LicensePlate", QueryComparisons.Equal, LicensePlate));
            TableContinuationToken continuationToken = null;
            do
            {
                TableQuerySegment<VehicleEntity> querySegment = await table.ExecuteQuerySegmentedAsync(query, continuationToken);
                continuationToken = querySegment.ContinuationToken;

                foreach (VehicleEntity qEntity in querySegment.Results)
                {
                    var deleteOperation = TableOperation.Delete(qEntity);
                    await table.ExecuteAsync(deleteOperation);
                    ResultMessage += $"\nLicense Plate: {qEntity.LicensePlate}.";
                }

            } while (continuationToken != null);

            // TODO: Delete the URL of this user.
            // String uniqeUrl = DefaultUrl + LicensePlate;

            return new OkObjectResult(ResultMessage);
        }

        /* 
         * Function UpdateVehicleLocation: receives vehicle updated location from the IoT camera and then does the following:
         * 1. Updates Azure tables about vehicle entity new location
         * 2. Sends SignalR to the vehicle assigned URL to update its location on the web app.
         */
        [FunctionName("UpdateVehicleLocation")]
        public static async Task<IActionResult> UpdateVehicleLocation(
            [HttpTrigger(AuthorizationLevel.Anonymous, "get", "post", Route = "UpdateVehicleLocation")] HttpRequest req,
            [SignalR(HubName = "ParkingChat")] IAsyncCollector<SignalRMessage> signalRMessages,
            ILogger log)
        {
            log.LogInformation("UpdateVehicleLocation function processed a request.");

            // Retrieve the storage account connection string from the app settings, parse and create a reference to the table
            string storageConnectionString = Environment.GetEnvironmentVariable("AzureWebJobsStorage");
            log.LogInformation("Storage connection string: {storageConnectionString}", storageConnectionString);

            CloudStorageAccount storageAccount = CloudStorageAccount.Parse(storageConnectionString);
            CloudTableClient tableClient = storageAccount.CreateCloudTableClient();
            CloudTable table = tableClient.GetTableReference("ParkingSectionsOccupancy");

            // Get the license plate from the request
            log.LogInformation("taking req info");
            string LicensePlate = req.Form["LicensePlate"];
            string Section = req.Form["Section"];
            int Floor = Int32.Parse(req.Form["Floor"]);


            log.LogInformation("Received request for License Plate: {LicensePlate}, Section: {Section}, Floor: {Floor}", LicensePlate, Section, Floor);

            // Create a retrieve operation that takes a partition key and a row key
            TableQuery<VehicleEntity> query = new TableQuery<VehicleEntity>()
                .Where(TableQuery.GenerateFilterCondition("LicensePlate", QueryComparisons.Equal, LicensePlate))
                .Take(1); // Retrieve only one entity

            TableContinuationToken continuationToken = null;
            List<VehicleEntity> entities = new List<VehicleEntity>();

            do
            {
                TableQuerySegment<VehicleEntity> queryResult = await table.ExecuteQuerySegmentedAsync(query, continuationToken);
                entities.AddRange(queryResult.Results);
                continuationToken = queryResult.ContinuationToken;
            } while (continuationToken != null);

            // Get the latest entity (if any)
            VehicleEntity entity = entities.FirstOrDefault();

            // Check if a vehicle entity was found
            if (entity == null)
            {
                log.LogInformation("Vehicle with License Plate: {LicensePlate} not found", LicensePlate);
                return new NotFoundResult();
            }

            log.LogInformation("Latest entity found for License Plate: {LicensePlate}", LicensePlate);

            // Update the entity relevant attributes
            entity.Section = Section;
            entity.Floor = Floor;

            // 1.
            // Update the entity in the table
            TableOperation updateOperation = TableOperation.Replace(entity);
            await table.ExecuteAsync(updateOperation);

            log.LogInformation("Entity updated in Azure Table for License Plate: {LicensePlate}", LicensePlate);

            // 2.
            // Update the user's map using Azure SignalR
            string mapUpdateValue = $"F{Floor}_{Section}";
            await signalRMessages.AddAsync(new SignalRMessage
            {
                // UserId = LicensePlate, // Or replace with the appropriate user ID
                Target = "UpdateMap",
                Arguments = new object[] { LicensePlate, mapUpdateValue }
            });

            log.LogInformation("SignalR message sent to update map for License Plate: {LicensePlate}", LicensePlate);

            string responseMessage = $"This HTTP trigger function executed successfully. License Plate: {LicensePlate} changed position to Floor: {Floor}, Section: {Section}.";
            return new OkObjectResult(responseMessage);
        }


        /*
         * Function: Query the database about parking lot occupancy
         */
        [FunctionName("QueryOccupancy")]
        public static async Task<IActionResult> QueryOccupancy(
        [HttpTrigger(AuthorizationLevel.Anonymous, "get", "post", Route = "QueryOccupancy")] HttpRequest req,
        [SignalR(HubName = "ParkingChat")] IAsyncCollector<SignalRMessage> signalRMessages,
        ILogger log)
        {
            // Retrieve the storage account connection string from the app settings, parse and create a reference to the table
            string storageConnectionString = Environment.GetEnvironmentVariable("AzureWebJobsStorage");
            CloudStorageAccount storageAccount = CloudStorageAccount.Parse(storageConnectionString);
            CloudTableClient tableClient = storageAccount.CreateCloudTableClient();
            CloudTable table = tableClient.GetTableReference("ParkingSectionsOccupancy");
            log.LogInformation("Started occupancy query operation");

            // Query the database to get the count of entries per floor
            var query = new TableQuery<VehicleEntity>();
            var queryResult = await table.ExecuteQuerySegmentedAsync(query, null);

            // Calculate the count of entries per floor
            var floorCounts = queryResult.Results
                .GroupBy(entity => entity.Floor)
                .Select(group => new { Floor = group.Key, Count = group.Count() })
                .ToList();

            log.LogInformation("query result received");

            // Send the floor counts to the user with SignalR
            await signalRMessages.AddAsync(new SignalRMessage
            {
                // TODO: implement users in the website
                // UserId = req.Query["LicensePlate"],
                Target = "UpdateOccupancy",
                Arguments = new object[] { floorCounts.Select(fc => new { fc.Floor, fc.Count }).ToArray() }
            });

            log.LogInformation("sent signalr message");

            string responseMessage = $"This HTTP Trigger function executed successfully. Occupancy data for each floor sent.";
            return new OkObjectResult(responseMessage);
        }


        [FunctionName("negotiate")]
        public static SignalRConnectionInfo Negotiate(
            [HttpTrigger(AuthorizationLevel.Anonymous, "get", "post")] HttpRequest req,
            [SignalRConnectionInfo(HubName = "ParkingChat")] SignalRConnectionInfo connectionInfo)
        {
            return connectionInfo;
        }
    }

    public class VehicleEntity : TableEntity
    {
        public string LicensePlate { get; set; }
        public string Section { get; set; }
        public Int32 Floor { get; set; }
    }
}
