
UPLOAD_FOLDER = "./uploads"  # Define the folder for saving images

class AdminResource(Resource):
    def post(self):
        # Ensure the uploads directory exists
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)  # Create the directory if it doesn't exist

        # Check if an image was uploaded
        if 'admin_image' not in request.files:
            return {'message': 'No image file provided'}, 400

        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Handle the file upload
        admin_image = request.files['admin_image']
        
        if admin_image:
            filename = secure_filename(admin_image.filename)  # Sanitize the filename
            file_path = os.path.join(UPLOAD_FOLDER, filename)  # Define the file path
            admin_image.save(file_path)  # Save the file

            admin_image_url = file_path  # Use the saved path
        else:
            admin_image_url = None  # If no image is provided

        # Simulating saving the admin details (Replace with actual database saving logic)
        try:
            new_admin = {
                "name": name,
                "email": email,
                "password": password,
                "admin_image": admin_image_url
            }
            # new_admin.save()  # Uncomment when using a database
            return {'message': 'Admin registered successfully', 'data': new_admin}, 201
        except Exception as e:
            return {'message': f"Error: {str(e)}"}, 500