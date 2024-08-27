from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect, get_object_or_404
from cart.models import Cart, CartItem
from cart.cart_items import add_product_to_cart_history, your_cart_items
from collections import Counter
from django.http import JsonResponse
from decimal import Decimal
from django.contrib import messages
from checkout.models import Payment


def add_to_cart(request, content_id, product_id):
    if "user_id" in request.session:
        add_to_cart_helper(request, content_id, product_id)
        return redirect("cart:cart_view")
    else:
        messages.info(request, "Your session has expired, please log-in first!")
        return redirect("Homepage:login")


def remove_from_cart(request, content_id, product_id):
    if request.method == "GET":
        if "user_id" and "cart_items" in request.session:
            content_type = ContentType.objects.get_for_id(content_id)
            # cart = Cart.objects.get(user=request.user)

            cart = (
                Cart.objects.filter(user=request.user)
                .exclude(cart_payment__isnull=False)
                .select_related("user")
            )

            cart = cart.first()

            cart_item = CartItem.objects.get(
                cart=cart, content_type=content_type, object_id=product_id
            )
            if cart_item.quantity > 1:
                cart_item.quantity = cart_item.quantity - 1
            else:
                cart_item.delete()

            # Update cart totals
            cart.subtotal = cart.subtotal - cart_item.price
            cart.total = cart.total - cart_item.price
            cart.save()
            cart_item.save()

            # delete product and content type from the cookie
            cookie_cart = request.session.get("cart_items")
            prompted_list = [content_id, product_id]
            print(f"&&&&&&&&&&&&&&&{prompted_list}")

            # 2. Identify the index of the list that matches the prompted list
            index_to_remove = None
            for i, item in enumerate(cookie_cart):
                if item == prompted_list:
                    index_to_remove = i
                    break

            # 3. If found, remove that list from the cart_items list
            if index_to_remove is not None:
                del cookie_cart[index_to_remove]
            print(f"%%%%%%%%%%%%5{cookie_cart}")

            response = redirect("cart:cart_view")
            # response.set_cookie("sessionid", {"cart_items": cookie_cart}, httponly=True)
            request.session["cart_items"] = cookie_cart
            print(f"^^^^^^^^^^^^^^^6{request.session.get('cart_items')}")
            return response

    else:
        return JsonResponse({"message": "Invalid request"})


def cart_view(request):
    if "user_id" in request.session and "cart_items" in request.session:
        cart_items = your_cart_items(request)

        # cart = Cart.objects.get(user=request.user)
        # if cart:
        #     cart_items_ = cart.cartitem_set.all()

        Content_Type_id = []
        product_id = []

        for items in cart_items:
            Content_Type_id.append(items[0])
            product_id.append(items[1])

        # Combine content_type_id and product_id into tuples
        combined_data = list(zip(Content_Type_id, product_id))
        # Count occurrences using Counter
        counted_data = Counter(combined_data)
        # Create a list of tuples with count, content_type_id, and product_id

        results = []

        for key, count in counted_data.items():
            content_type = ContentType.objects.get_for_id(id=key[0])
            if content_type.app_label == "i":
                product = content_type.get_object_for_this_type(monitor_id=key[1])
            else:
                product = content_type.get_object_for_this_type(id=key[1])
            results.append((count, key[0], key[1], product))
        print(results)

        cart_total = 0
        for item in results:
            product = item[3]
            cart_total += product.price * item[0]  # item[0] is the count of the product

        return render(
            request,
            "cart.html",
            {
                # "cart_items": cart_items_,
                # "cart": cart,
                "cart_items": len(results),
                "sub_total": cart_total,
                "total_amount": cart_total + 53,
                "results": results,
                "tax": 53.99,
            },
        )
    else:
        return render(request, "cart.html", {"results": None})


def add_to_cart_helper(request, content_type_id, product_id):
    content_type = ContentType.objects.get_for_id(id=content_type_id)

    model_class = get_model_name(content_type_id)

    product = get_object_or_404(model_class, pk=product_id)
    user_id = request.session.get("user_id")

    cart = (
        Cart.objects.filter(user=request.user)
        .exclude(cart_payment__isnull=False)
        .select_related("user")
    )

    if not cart.exists():
        cart = Cart.objects.create(user=request.user)
    else:
        cart = cart.first()

    cart_item, cart_item_created = CartItem.objects.get_or_create(
        cart=cart,
        content_type=content_type,
        object_id=product_id,
        quantity=1,
        price=product.price,
    )

    if not cart_item_created:
        # If the cart item already exists, update the quantity and price
        cart_item.quantity += 1
        cart_item.save()

    cart.subtotal = Decimal(cart.subtotal) + Decimal(product.price).quantize(
        Decimal("1.00")
    )
    cart.total = Decimal(cart.total) + Decimal(product.price).quantize(Decimal("1.00"))
    cart.save()

    cart_items_in_cookie = [content_type_id, product_id]
    add_product_to_cart_history(request, cart_items_in_cookie)


def get_model_name(content_type_id):
    try:
        content_type = ContentType.objects.get(id=content_type_id)
        model_class = content_type.model_class()
        return model_class
    except ContentType.DoesNotExist:
        return None
