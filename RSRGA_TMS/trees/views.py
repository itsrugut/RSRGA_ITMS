import csv
import json
import logging
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from RSRGA_TMS.trees.models import TreeType, TreeStatus, Tree
from RSRGA_TMS.trees.serializers import TreeSerializer, PlanterSerializer, TreeStatusSerializer, TreeTypeSerializer
from RSRGA_TMS.users.models import Planter


# Create your views here.
def interactive_mapping(request):
    tree_types = TreeType.objects.all()
    tree_statuses = TreeStatus.objects.all()
    # planters = Planter.objects.all()

    context = {
        'tree_types': tree_types,
        'tree_statuses': tree_statuses,
        # 'planters': planters,
    }
    return render(request, 'map/map.html')


@login_required
def tree_inventory(request):
    # Get all tree types and statuses for the filters
    tree_types = TreeType.objects.all()
    tree_statuses = TreeStatus.objects.all()

    # Get filter parameters from GET request
    type_filter = request.GET.get('type_filter')
    status_filter = request.GET.get('status_filter')

    # Filter trees based on the selected filters
    trees = Tree.objects.all()

    if type_filter:
        trees = trees.filter(treetype__typeid=type_filter)
    if status_filter:
        trees = trees.filter(status__statusid=status_filter)

    context = {
        'trees': trees,
        'tree_types': tree_types,
        'tree_statuses': tree_statuses,
        'type_filter': type_filter,
        'status_filter': status_filter,
    }
    return render(request, 'tree_inventory/tree_inventory.html', context)


def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file', None)

        # Check if file is selected
        if not csv_file:
            messages.error(request, "No file selected.")
            return redirect('upload_csv')

        # Check if file is a CSV
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "File is not a CSV.")
            return redirect('upload_csv')

        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                try:
                    # Extract fields from the row
                    pointname = row['Point Name']
                    commonname = row['Common Name']
                    latitude = float(row['Latitude'])
                    longitude = float(row['Longitude'])
                    planter = row['Planter']
                    statusname = row['Status']
                    dateplanted = row['Date Planted']  # The 'Planted Date' column

                    # Debugging: Log the row being processed
                    print(f"Processing row: {row}")

                    # Convert 'Planted Date' to a date object (ensure it's in the correct format)
                    try:
                        dateplanted = datetime.strptime(dateplanted, '%d/%m/%Y').date()  # '10/12/2023' format
                    except ValueError:
                        print(f"Invalid date format for row {row}. Expected format: YYYY-MM-DD")
                        messages.error(request, f"Invalid date format for row {row}. Expected format: YYYY-MM-DD")
                        continue  # Skip this row and continue with the next

                    # Fetch related objects from the database
                    try:
                        treetype = TreeType.objects.get(commonname=commonname)
                        print(f"Found TreeType: {treetype}")
                    except TreeType.DoesNotExist:
                        print(f"TreeType '{commonname}' does not exist.")
                        messages.error(request, f"TreeType '{commonname}' does not exist.")
                        continue  # Skip this row and continue with the next

                    # Handle Planter with single or full name
                    try:
                        planternames = planter.split(' ', 1)

                        if len(planternames) == 1:
                            firstname = planternames[0]
                            lastname = ""
                        else:
                            firstname, lastname = planternames

                        planter = Planter.objects.get(firstname__iexact=firstname, lastname__iexact=lastname)
                        print(f"Found Planter: {planter}")
                    except Planter.DoesNotExist:
                        print(f"Planter '{planter}' does not exist.")
                        messages.error(request, f"Planter '{planter}' does not exist.")
                        continue  # Skip this row and continue with the next

                    # Fetch TreeStatus
                    try:
                        status = TreeStatus.objects.get(statusname__iexact=statusname)
                        print(f"Found TreeStatus: {status}")
                    except TreeStatus.DoesNotExist:
                        print(f"TreeStatus '{statusname}' does not exist.")
                        messages.error(request, f"TreeStatus '{statusname}' does not exist.")
                        continue  # Skip this row and continue with the next

                    # Create a new tree object in the database
                    Tree.objects.create(
                        pointname=pointname,
                        treetype=treetype,
                        location=Point(longitude, latitude),
                        planterid=planter,
                        status=status,
                        dateplanted=dateplanted  # Use the converted planted date
                    )
                    print(f"Tree created: {pointname}, {commonname}")

                except Exception as e:
                    # Log any unexpected errors
                    print(f"Error processing row {row}: {e}")
                    messages.error(request, f"Error processing row {row}. Error: {e}")

            # If no errors occur, show a success message
            messages.success(request, "CSV processed successfully!")
            return redirect('upload_csv')

        except Exception as e:
            # General error when reading or decoding the CSV file
            print(f"An error occurred while processing the file: {e}")
            messages.error(request, f"An error occurred while processing the file: {e}")
            return redirect('upload_csv')

    return render(request, 'tree_inventory/upload_csv.html')


def export_tree_inventory_csv(request):
    # Create the HttpResponse object with the appropriate CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tree_inventory.csv"'

    writer = csv.writer(response)
    # Write the header row
    writer.writerow([
        'Tree ID', 'Point Name', 'Tree Type', 'Latitude', 'Longitude', 'Status', 'Date Planted', 'Planter'
    ])

    # Write the data rows
    trees = Tree.objects.select_related('treetype', 'status', 'planterid').all()
    for tree in trees:
        writer.writerow([
            tree.treeid,
            tree.pointname or "N/A",
            tree.treetype.commonname or "Unknown",
            tree.location.y if tree.location else "N/A",
            tree.location.x if tree.location else "N/A",
            tree.status.statusname or "No Status",
            tree.dateplanted,
            f"{tree.planterid.firstname} {tree.planterid.lastname}".strip() or "Unknown"
        ])

    return response


def get_trees(request):
    trees = Tree.objects.all()
    tree_data = []
    for tree in trees:
        # Check for the presence of firstname and lastname
        firstname = tree.planterid.firstname if tree.planterid.firstname else ""
        lastname = tree.planterid.lastname if tree.planterid.lastname else ""

        # Build the planter name based on available fields
        if firstname and lastname:
            planter_name = f"{firstname} {lastname}"
        elif firstname:
            planter_name = firstname
        elif lastname:
            planter_name = lastname
        else:
            planter_name = "Unknown"

        # Append tree data with the constructed planter name
        tree_data.append({
            'treeid': tree.treeid,
            'pointname': tree.pointname,
            'commonname': tree.treetype.commonname,
            'scientificname': tree.treetype.scientificname,
            'localname': tree.treetype.localname,
            'latitude': tree.location.y,  # Assuming you're using GeoDjango PointField
            'longitude': tree.location.x,
            'status': tree.status.statusname,
            'planter': planter_name,
            'affiliation': tree.planterid.affiliation,
            'dateplanted': tree.dateplanted,
        })

    return JsonResponse(tree_data, safe=False)


@csrf_exempt
def add_tree(request):
    if request.method == 'POST':
        logging.debug(f"Received POST data: {request.POST}")

        # Check if the content type is JSON
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {str(e)}")
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        else:
            # If not JSON, use the POST data
            data = request.POST.dict()

        logging.debug(f"Parsed data: {data}")

        try:
            new_tree = Tree.objects.create(
                treetype=TreeType.objects.get(typeid=data['treetype']),
                pointname=data['pointname'],
                location=Point(float(data['longitude']), float(data['latitude'])),
                status=TreeStatus.objects.get(statusid=data['status']),
                dateplanted=data['dateplanted'],
                planterid=Planter.objects.get(planterid=data['planterid'])
            )

            return JsonResponse({
                'treeid': new_tree.treeid,
                'treetype': new_tree.treetype.commonname,
                'pointname': new_tree.pointname,
                'latitude': new_tree.location.y,
                'longitude': new_tree.location.x,
                'status': new_tree.status.statusname,
                'planter': f"{new_tree.planterid.firstname} {new_tree.planterid.lastname}"
            }, status=201)
        except Exception as e:
            logging.error(f"Error in add_tree view: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


class TreeTypeList(generics.ListAPIView):
    queryset = TreeType.objects.all()
    serializer_class = TreeTypeSerializer


class TreeStatusList(generics.ListAPIView):
    queryset = TreeStatus.objects.all()
    serializer_class = TreeStatusSerializer


def get_planters(request):
    planters = Planter.objects.all()
    planters_data = PlanterSerializer(planters, many=True).data
    return JsonResponse(planters_data, safe=False)


class AddTree(generics.CreateAPIView):
    serializer_class = TreeSerializer

    def create(self, request, *args, **kwargs):
        # Extract longitude and latitude from the request data
        longitude = request.data.get('longitude')
        latitude = request.data.get('latitude')

        # Create a new dictionary with all the data, including the Point object
        tree_data = request.data.copy()
        tree_data['location'] = Point(float(longitude), float(latitude))

        serializer = self.get_serializer(data=tree_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


def get_tree_details(request, tree_id):
    try:
        tree = Tree.objects.get(treeid=tree_id)
        tree_data = TreeSerializer(tree).data
        return JsonResponse(tree_data, safe=False, status=200)
    except Tree.DoesNotExist:
        return JsonResponse({'error': 'Tree not found'}, status=404)


@api_view(['PUT'])
def update_tree_details(request, tree_id):
    """
    Update the tree status, tree type (common name), and point name for a specific tree.
    """
    try:
        tree = get_object_or_404(Tree, treeid=tree_id)
    except Tree.DoesNotExist:
        return Response({'error': 'Tree not found'}, status=status.HTTP_404_NOT_FOUND)

    # Extract data from request
    status_id = request.data.get('status')
    common_name = request.data.get('commonname')
    point_name = request.data.get('pointname')

    if not status_id and not common_name and not point_name:
        return Response({'error': 'At least one field (status, common name, or point name) is required'},
                        status=status.HTTP_400_BAD_REQUEST)

    # ✅ Update Status if provided
    if status_id:
        try:
            new_status = TreeStatus.objects.get(statusid=status_id)
            tree.status = new_status
        except TreeStatus.DoesNotExist:
            return Response({'error': 'Invalid status ID'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Update Tree Type (Common Name) if provided
    if common_name:
        try:
            tree_type = TreeType.objects.get(commonname=common_name)
            tree.treetype = tree_type
        except TreeType.DoesNotExist:
            return Response({'error': 'Invalid common name'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Update Point Name if provided
    if point_name:
        tree.pointname = point_name

    # Save updates
    tree.save()
    return Response({'message': 'Tree details updated successfully'}, status=status.HTTP_200_OK)


def search_trees(request):
    try:
        query = request.GET.get('q', '').strip()  # Remove spaces
        if not query:
            return JsonResponse({'error': 'Search query cannot be empty.'}, status=400)

        # Split the query into words for multi-word searches
        query_words = query.split()

        # Start with an empty Q object
        q_object = Q()

        # If we have a single word query, use the original search logic
        if len(query_words) == 1:
            q_object = (
                    Q(pointname__icontains=query) |
                    Q(planterid__firstname__icontains=query) |
                    Q(planterid__lastname__icontains=query) |
                    Q(planterid__affiliation__icontains=query) |
                    Q(treetype__commonname__icontains=query) |
                    Q(treetype__scientificname__icontains=query) |
                    Q(treetype__localname__icontains=query) |
                    Q(treetype__uses__icontains=query) |
                    Q(treetype__description__icontains=query) |
                    Q(dateplanted__icontains=query)
            )
        else:
            # For multi-word queries, add specific handling for full names
            # Try to match the full query string against multiple fields
            q_object |= (
                    Q(pointname__icontains=query) |
                    Q(planterid__affiliation__icontains=query) |
                    Q(treetype__commonname__icontains=query) |
                    Q(treetype__scientificname__icontains=query) |
                    Q(treetype__localname__icontains=query) |
                    Q(treetype__uses__icontains=query) |
                    Q(treetype__description__icontains=query)
            )

            # Special handling for first name + last name combinations
            if len(query_words) == 2:
                # Try first word as first name, second word as last name
                q_object |= (Q(planterid__firstname__icontains=query_words[0]) &
                             Q(planterid__lastname__icontains=query_words[1]))

                # Also try in reverse (in case last name is entered first)
                q_object |= (Q(planterid__firstname__icontains=query_words[1]) &
                             Q(planterid__lastname__icontains=query_words[0]))

        trees = Tree.objects.filter(q_object).distinct()

        if not trees.exists():
            return JsonResponse({'message': 'No trees found matching your search.'}, status=404)

        tree_data = []
        for tree in trees:
            tree_data.append({
                'treeid': tree.treeid,
                'pointname': tree.pointname,
                'commonname': tree.treetype.commonname,
                'scientificname': tree.treetype.scientificname,
                'localname': tree.treetype.localname,
                'latitude': tree.location.y,
                'longitude': tree.location.x,
                'status': tree.status.statusname,
                'planter': f"{tree.planterid.firstname} {tree.planterid.lastname}",
                'affiliation': tree.planterid.affiliation,
                'dateplanted': tree.dateplanted.strftime("%Y-%m-%d"),
            })

        return JsonResponse(tree_data, safe=False, status=200)

    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}. Please try again later.'}, status=500)