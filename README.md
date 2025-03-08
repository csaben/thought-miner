# thought-miner


# transcription
> run from thought-miner/  (to handle using parent dir `data-access` lib)
```
sudo docker build -f thought-miner-transcribe/Dockerfile .  
```


## First Run

To set up the project for the first time, follow these steps:

1. **Build and Start Services**:
   ```bash
   sudo docker-compose -f docker-compose.test.yml up --build
   ```

2. **Run Database Migrations** (if applicable):
   ```bash
   npx prisma db push
   ```

3. **Access the Application**:
   - The application will be available at `http://localhost:3000`.

## Stopping Services

To stop the services, run: