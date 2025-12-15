# MongoDB Connection String - Important Note

## ⚠️ Your MongoDB URI Needs Authentication

I noticed your MongoDB connection string from the screenshot:
```
cluster0.yfuwlmd.mongodb.net/Sumarize
```

This is **incomplete**. MongoDB Atlas requires a username and password.

## ✅ How to Get the Complete Connection String

1. Open **MongoDB Compass** (you already have it)
2. Click on your connection: `cluster0.yfuwlmd.mongodb.net`
3. Look for the **full connection string** which should look like:

```
mongodb+srv://USERNAME:PASSWORD@cluster0.yfuwlmd.mongodb.net/Sumarize
```

OR

3. Go to MongoDB Atlas website: https://cloud.mongodb.com/
4. Click **"Connect"** on your cluster
5. Choose **"Connect your application"**
6. Copy the connection string
7. Replace `<password>` with your actual password

## 📝 Update Your .env File

Open `.env` and replace the MongoDB URI with the complete string:

```bash
# Before (incomplete):
MONGODB_URI=mongodb+srv://cluster0.yfuwlmd.mongodb.net/Sumarize

# After (complete):
MONGODB_URI=mongodb+srv://your_username:your_password@cluster0.yfuwlmd.mongodb.net/Sumarize
```

**Important**: 
- Replace `your_username` with your MongoDB username
- Replace `your_password` with your MongoDB password
- Keep `/Sumarize` at the end (this is your database name)

## 🔍 Example

If your username is `admin` and password is `MyPass123`, it would be:
```
MONGODB_URI=mongodb+srv://admin:MyPass123@cluster0.yfuwlmd.mongodb.net/Sumarize
```

---

Once you have:
1. ✅ Complete MongoDB connection string (with username:password)
2. ✅ LlamaParser API key

You can run: `npm start`
