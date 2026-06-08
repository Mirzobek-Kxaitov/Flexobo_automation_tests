# Frontend uchun `data-testid` atributlar qo'shish

## Bu nima?

`data-testid` — bu HTML elementga qo'shiladigan maxsus atribut. U faqat QA automation
testlari uchun ishlatiladi. Foydalanuvchiga ko'rinmaydi, sayt ishlashiga ta'sir
qilmaydi, CSS ga aloqasi yo'q.

```html
<!-- Oddiy button -->
<button>Add Truck</button>

<!-- data-testid qo'shilgan button — faqat shu atribut qo'shiladi, boshqa hech narsa o'zgarmaydi -->
<button data-testid="fleet_add_truck_button">Add Truck</button>
```

Shunchaki har bir kerakli elementga bitta `data-testid="nom"` qo'shiladi, tamom.

---

## Nima uchun kerak?

Hozir QA testlari elementlarni **matn** bo'yicha topadi:

```python
# Test: "Sign In" yozuvi bor buttonni top
page.get_by_role("button", name="Sign In")
```

Agar siz button matnini `"Sign In"` dan `"Log In"` ga o'zgartirsangiz — **test sinadi**,
lekin bu bug emas. Shuning uchun testlar matn yoki CSS ga emas, `data-testid` ga tayanishi
kerak. `data-testid` qo'shilsa — siz UI matnini, stilini, joylashuvini xohlagancha
o'zgartirishingiz mumkin, testlar sinmaydi.

---

## Qanday qo'shiladi? (qadam-qadam)

### 1-qadam: Oddiy element

Elementga `data-testid="nom"` atribut qo'shing:

```tsx
// OLDIN
<button onClick={handleLogin}>Sign In</button>

// KEYIN — faqat data-testid qo'shildi
<button data-testid="login_submit_button" onClick={handleLogin}>Sign In</button>
```

**Input uchun:**
```tsx
// OLDIN
<input type="email" placeholder="Email or phone number" />

// KEYIN
<input data-testid="login_email_input" type="email" placeholder="Email or phone number" />
```

**Select / Dropdown uchun:**
```tsx
// OLDIN
<select>
  <option>Uzbekistan</option>
</select>

// KEYIN
<select data-testid="fleet_country_select">
  <option>Uzbekistan</option>
</select>
```

**Tab uchun:**
```tsx
// OLDIN
<Tab>Trucks</Tab>

// KEYIN
<Tab data-testid="fleet_trucks_tab">Trucks</Tab>
```

**Modal / Container uchun:**
```tsx
// OLDIN
<div className="modal">
  <p>Are you sure?</p>
  <button>Delete</button>
</div>

// KEYIN
<div data-testid="fleet_delete_confirm_modal" className="modal">
  <p>Are you sure?</p>
  <button data-testid="fleet_delete_confirm_button">Delete</button>
</div>
```

### 2-qadam: Dinamik element (ro'yxatdagi har bir element)

Agar elementlar ro'yxatda bo'lsa (masalan, truck lari, load lari) — har biriga
**backend id** qo'shiladi:

```tsx
// Masalan trucks ro'yxatini render qilayotgan joyda:
{trucks.map((truck) => (
  <div data-testid={`fleet_truck_row_${truck.id}`} key={truck.id}>
    <span>{truck.govNumber}</span>
    <button data-testid={`fleet_truck_actions_button_${truck.id}`}>
      ...
    </button>
  </div>
))}
```

Bu yerda `truck.id` backend dan keladi. Masalan natija:
```html
<div data-testid="fleet_truck_row_abc123">...</div>
<div data-testid="fleet_truck_row_def456">...</div>
```

### 3-qadam: Shadcn/Headless UI componentlar

Agar loyihada Shadcn, Radix, yoki Headless UI ishlatilsa — componentlarga props
sifatida beriladi va ular avtomatik DOM ga o'tadi:

```tsx
// Shadcn Button
<Button data-testid="loads_publish_button">Publish</Button>

// Shadcn Dialog
<AlertDialog>
  <AlertDialogTrigger data-testid="roles_delete_button">Delete</AlertDialogTrigger>
  <AlertDialogContent data-testid="roles_delete_confirm_modal">
    <AlertDialogAction data-testid="roles_delete_confirm_button">
      Confirm
    </AlertDialogAction>
  </AlertDialogContent>
</AlertDialog>

// Shadcn Tabs
<TabsTrigger data-testid="fleet_trucks_tab" value="trucks">Trucks</TabsTrigger>

// Shadcn DropdownMenu
<DropdownMenuTrigger data-testid="global_user_menu_button">
  <Avatar />
</DropdownMenuTrigger>
<DropdownMenuItem data-testid="global_logout_menu_item">
  Logout
</DropdownMenuItem>
```

> Shadcn/Radix componentlari `data-*` atributlarni avtomatik DOM ga o'tkazadi.
> Siz shunchaki props sifatida bersangiz bo'ldi.

---

## Naming qoidalari

| Qoida | Misol |
|-------|-------|
| Format: `sahifa_element_vazifa` | `fleet_add_truck_button` |
| Hamma narsa `snake_case`, kichik harf | `loads_from_input` (LoadsFromInput emas) |
| Button = `_button` | `login_submit_button` |
| Input / Textarea = `_input` | `login_email_input` |
| Select / Dropdown = `_select` yoki `_dropdown` | `fleet_country_select` |
| Tab = `_tab` | `fleet_trucks_tab` |
| Menu item = `_menu_item` | `global_add_load_menu_item` |
| Container / Page = `_page`, `_modal`, `_form` | `loads_place_bid_form` |
| Dinamik = `_${entity.id}` | `fleet_truck_row_${truck.id}` |

---

## Tekshirish

`data-testid` to'g'ri qo'shilganini tekshirish uchun — brauzerdagi DevTools > Elements
panelda elementni topib, `data-testid` atribut borligini ko'ring:

```html
<button data-testid="login_submit_button" class="btn btn-primary">Sign In</button>
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
              shu atribut bo'lishi kerak
```

---

## To'liq ro'yxat

Quyida **barcha** kerakli elementlar sahifa bo'yicha guruhlangan. `data-testid` ustunidagi
nomni aynan shu ko'rinishda qo'ying.

Belgilar:
- **Statik** — har doim bitta element (masalan, "Add Truck" button)
- **Dinamik** — ro'yxatdagi har bir element uchun alohida (`${id}` bilan)

---

### 1. Login sahifasi (`/sign-in`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Email / telefon input | input | `login_email_input` |
| Parol input | input | `login_password_input` |
| Sign In button | button | `login_submit_button` |
| Xato xabar (noto'g'ri login) | text | `login_error_message` |

---

### 2. Global / Header (har bir sahifada)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Cookie banner Accept button | button | `global_cookie_accept_button` |
| Header "Add" button | button | `global_add_button` |
| Add menu > Load | menu item | `global_add_load_menu_item` |
| Add menu > Transport | menu item | `global_add_transport_menu_item` |
| User avatar / profile dropdown trigger | button | `global_user_menu_button` |
| Logout menu item | menu item | `global_logout_menu_item` |
| Logout tasdiqlash modali | container | `global_logout_confirm_modal` |
| Logout "Yes" button | button | `global_logout_confirm_button` |

---

### 3. Top Navigation (header menyu)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Load link | link | `top_nav_load_link` |
| Transport link | link | `top_nav_transport_link` |
| Rating link | link | `top_nav_rating_link` |
| Blog link | link | `top_nav_blog_link` |
| Pricing link | link | `top_nav_pricing_link` |
| Currency dropdown | dropdown | `top_nav_currency_dropdown` |
| Language dropdown | dropdown | `top_nav_language_dropdown` |
| Notifications button | button | `top_nav_notifications_button` |
| Messages button | button | `top_nav_messages_button` |

---

### 4. Sidebar / Profile navigatsiya

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Profile link | menu item | `sidebar_profile_link` |
| My Loads link | menu item | `sidebar_my_loads_link` |
| My Trips link | menu item | `sidebar_my_trips_link` |
| Fleet link | menu item | `sidebar_fleet_link` |
| Drivers link | menu item | `sidebar_drivers_link` |
| Orders link | menu item | `sidebar_orders_link` |
| My Bids link | menu item | `sidebar_my_bids_link` |
| Received Bids link | menu item | `sidebar_received_bids_link` |
| Usage link | menu item | `sidebar_usage_link` |

---

### 5. Fleet sahifasi (`/tms/fleet`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Fleet sahifa | page | `fleet_page` |
| Trucks tab | tab | `fleet_trucks_tab` |
| Trailers tab | tab | `fleet_trailers_tab` |
| Add Truck button | button | `fleet_add_truck_button` |
| Add Trailer button | button | `fleet_add_trailer_button` |
| Country select | select | `fleet_country_select` |
| Country search input | input | `fleet_country_search_input` |
| Brand select | select | `fleet_brand_select` |
| Year select | select | `fleet_year_select` |
| Gov number input | input | `fleet_gov_number_input` |
| Technical passport input | input | `fleet_technical_passport_input` |
| Lifting capacity select | select | `fleet_lifting_capacity_select` |
| Trailer type select | select | `fleet_trailer_type_select` |
| Loading types select | select | `fleet_loading_types_select` |
| Volume input (m3) | input | `fleet_volume_input` |
| Length input | input | `fleet_length_input` |
| Width input | input | `fleet_width_input` |
| Height input | input | `fleet_height_input` |
| Add/Save button (forma ichida) | button | `fleet_form_submit_button` |
| Cancel button (forma ichida) | button | `fleet_form_cancel_button` |
| Truck row | dinamik | `fleet_truck_row_${truck.id}` |
| Truck actions menu (3 nuqta) | dinamik | `fleet_truck_actions_button_${truck.id}` |
| Trailer row | dinamik | `fleet_trailer_row_${trailer.id}` |
| Trailer actions menu (3 nuqta) | dinamik | `fleet_trailer_actions_button_${trailer.id}` |
| Delete tasdiqlash button | button | `fleet_delete_confirm_button` |
| Deactivate tasdiqlash button | button | `fleet_deactivate_confirm_button` |
| Detach trailer tasdiqlash | button | `fleet_detach_trailer_confirm_button` |
| Detach driver tasdiqlash | button | `fleet_detach_driver_confirm_button` |
| Muvaffaqiyat xabari (truck updated) | text | `fleet_success_message` |

---

### 6. Loads yaratish / tahrirlash (`/profile-load`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Sahifa | page | `loads_create_page` |
| From input | input | `loads_from_input` |
| To input | input | `loads_to_input` |
| Load type select | select | `loads_load_type_select` |
| Date button | button | `loads_date_button` |
| Load weight input | input | `loads_weight_input` |
| Next button | button | `loads_next_button` |
| Body step container | container | `loads_body_step` |
| Transport type select | select | `loads_transport_type_select` |
| Loading type select | select | `loads_loading_type_select` |
| Unloading type select | select | `loads_unloading_type_select` |
| Price input | input | `loads_price_input` |
| Payment step container | container | `loads_payment_step` |
| Publish button | button | `loads_publish_button` |
| Muvaffaqiyat xabari | text | `loads_success_message` |
| Load actions menu (3 nuqta) | dinamik | `loads_load_actions_button_${load.id}` |
| Delete tasdiqlash | button | `loads_delete_confirm_button` |

---

### 7. Loads board / qidiruv (`/loads`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Loads sahifa | page | `loads_page` |
| Search From input | input | `loads_search_from_input` |
| Search To input | input | `loads_search_to_input` |
| Search button | button | `loads_search_button` |
| Filter button | button | `loads_filter_button` |
| Sort button | button | `loads_sort_button` |
| Filter panel | container | `loads_filter_panel` |
| Filter Apply button | button | `loads_filter_apply_button` |
| Filter Reset button | button | `loads_filter_reset_button` |
| Currency dropdown | dropdown | `loads_currency_dropdown` |
| Load tab | tab | `loads_tab_load_button` |
| Transport tab | tab | `loads_tab_transport_button` |
| Load card | dinamik | `loads_load_card_${load.id}` |
| Load card narx | dinamik | `loads_load_card_price_${load.id}` |
| Load card from shahar | dinamik | `loads_load_card_from_${load.id}` |
| Load card to shahar | dinamik | `loads_load_card_to_${load.id}` |
| Load detail sahifa | dinamik | `loads_detail_page_${load.id}` |

---

### 8. Bid qo'yish (load detail ichida)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Place a bid button (ochish) | button | `bid_place_open_button` |
| Bid form container | container | `bid_form_container` |
| Bid note textarea | input | `bid_form_note_input` |
| Bid date button | button | `bid_form_date_button` |
| Place bid submit button | button | `bid_form_submit_button` |
| Bid cancel button | button | `bid_form_cancel_button` |
| Bid muvaffaqiyat xabari | text | `bid_success_message` |

---

### 9. My Bids (`/my-bids`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| My Bids sahifa | page | `my_bids_page` |
| All tab | tab | `my_bids_all_tab` |
| Pending tab | tab | `my_bids_pending_tab` |
| Accepted tab | tab | `my_bids_accepted_tab` |
| Rejected tab | tab | `my_bids_rejected_tab` |
| On the way tab | tab | `my_bids_on_the_way_tab` |
| Delivered tab | tab | `my_bids_delivered_tab` |
| Bid card | dinamik | `my_bids_bid_card_${bid.id}` |
| Bid card narx | dinamik | `my_bids_bid_card_price_${bid.id}` |
| Bid status badge | dinamik | `my_bids_status_badge_${bid.id}` |

---

### 10. Received Bids

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Received Bids sahifa | page | `received_bids_page` |
| Received bids tab (profilda) | tab | `received_bids_tab` |
| All tab | tab | `received_bids_all_tab` |
| Pending tab | tab | `received_bids_pending_tab` |
| Accepted tab | tab | `received_bids_accepted_tab` |
| Rejected tab | tab | `received_bids_rejected_tab` |
| Bid card | dinamik | `received_bids_bid_card_${bid.id}` |
| Bid card narx | dinamik | `received_bids_card_price_${bid.id}` |
| Bid card ochish button | dinamik | `received_bids_open_button_${bid.id}` |
| Accept button | dinamik | `received_bids_accept_button_${bid.id}` |
| Reject button | dinamik | `received_bids_reject_button_${bid.id}` |

---

### 11. Trips yaratish / tahrirlash (`/trips`, `/profile-trips`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Trips sahifa | page | `trips_page` |
| Transport select | select | `trips_transport_select` |
| Unit / lifting capacity select | select | `trips_unit_select` |
| Volume input | input | `trips_volume_input` |
| Loading input | input | `trips_loading_input` |
| Loading radius input | input | `trips_loading_radius_input` |
| Unloading input | input | `trips_unloading_input` |
| Unloading radius input | input | `trips_unloading_radius_input` |
| Price input | input | `trips_price_input` |
| Next button | button | `trips_next_button` |
| Trip card | dinamik | `trips_trip_card_${trip.id}` |
| Trip actions menu (3 nuqta) | dinamik | `trips_trip_actions_button_${trip.id}` |
| Delete tasdiqlash | button | `trips_delete_confirm_button` |

---

### 12. Transport board (`/transport`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Transport sahifa | page | `transport_page` |
| Search From input | input | `transport_search_from_input` |
| Search To input | input | `transport_search_to_input` |
| Search button | button | `transport_search_button` |
| Filter button | button | `transport_filter_button` |
| Sort button | button | `transport_sort_button` |
| Currency dropdown | dropdown | `transport_currency_dropdown` |
| Transport card | dinamik | `transport_card_${trip.id}` |
| Transport card narx | dinamik | `transport_card_price_${trip.id}` |

---

### 13. Profile / Account (`/profile/root`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Profile sahifa | page | `profile_page` |
| Update Password button | button | `profile_update_password_button` |
| Verify Identity button | button | `profile_verify_identity_button` |
| Enable 2FA button | button | `profile_enable_2fa_button` |
| Roles tab | tab | `profile_roles_tab` |
| Users tab | tab | `profile_users_tab` |

---

### 14. Roles (`/profile/root` > Roles tab)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Create role button | button | `roles_create_button` |
| Role name input | input | `roles_name_input` |
| Role submit button | button | `roles_submit_button` |
| Role card | dinamik | `roles_role_card_${role.id}` |
| Role delete trigger | dinamik | `roles_delete_button_${role.id}` |
| Delete tasdiqlash button | button | `roles_delete_confirm_button` |

---

### 15. Users (`/profile/root` > Users tab)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Invite User button | button | `users_invite_button` |
| Pending Invitations tab | tab | `users_pending_invitations_tab` |
| Email / phone input | input | `users_invite_email_input` |
| Role select | select | `users_invite_role_select` |
| Send Invitation button | button | `users_send_invitation_button` |
| Invitation row | dinamik | `users_invitation_row_${invitation.id}` |
| Resend invitation button | dinamik | `users_resend_button_${invitation.id}` |
| Cancel invitation trigger | dinamik | `users_cancel_button_${invitation.id}` |
| Cancel tasdiqlash button | button | `users_cancel_confirm_button` |

---

### 16. Usage / Billing (`/usage`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Usage sahifa | page | `usage_page` |
| Hozirgi plan nomi | text | `usage_current_plan_label` |
| Upgrade plan button | button | `usage_upgrade_plan_button` |
| Bids placed card | card | `usage_bids_placed_card` |
| Bids placed qiymati | text | `usage_bids_placed_value` |
| Bookings card | card | `usage_bookings_card` |
| Contacts viewed card | card | `usage_contacts_viewed_card` |
| Team members card | card | `usage_team_members_card` |
| Storage used card | card | `usage_storage_used_card` |
| Fleet size card | card | `usage_fleet_size_card` |
| Active transport card | card | `usage_active_transport_card` |
| Company roles card | card | `usage_company_roles_card` |
| Company employees card | card | `usage_company_employees_card` |

---

### 17. Limit modal (limitga yetganda chiqadi)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Modal container | modal | `limit_modal_container` |
| Modal sarlavha | text | `limit_modal_title` |
| Modal xabar | text | `limit_modal_message` |
| Upgrade plan button | button | `limit_modal_upgrade_button` |
| Maybe later button | button | `limit_modal_maybe_later_button` |
| Close button | button | `limit_modal_close_button` |

---

### 18. TMS / Drivers (`/tms/drivers`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Drivers sahifa | page | `drivers_page` |
| Add Driver button | button | `drivers_add_button` |
| Invite Driver button | button | `drivers_invite_button` |
| Driver row | dinamik | `drivers_driver_row_${driver.id}` |
| Driver actions menu | dinamik | `drivers_driver_actions_button_${driver.id}` |

---

### 19. TMS / Orders (`/tms/orders`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Orders sahifa | page | `orders_page` |
| Order row | dinamik | `orders_order_row_${order.id}` |
| Order actions menu | dinamik | `orders_order_actions_button_${order.id}` |
| Order status | dinamik | `orders_order_status_${order.id}` |
| Order narx | dinamik | `orders_order_price_${order.id}` |

---

### 20. TMS / Delegations (`/tms/delegations`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Delegations sahifa | page | `delegations_page` |
| Invite partner button | button | `delegations_invite_partner_button` |
| Partner row | dinamik | `delegations_partner_row_${partner.id}` |
| Partner actions menu | dinamik | `delegations_partner_actions_button_${partner.id}` |

---

### 21. Calendar / Date picker (umumiy component)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Calendar container | container | `calendar_container` |
| Next month button | button | `calendar_next_month_button` |
| Mavjud kun | dinamik | `calendar_day_${yyyy_mm_dd}` |

---

### 22. Location autocomplete (umumiy component)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Suggestion ro'yxat | container | `location_suggestions_list` |
| Suggestion element | dinamik | `location_suggestion_${index}` |

---

### 23. Umumiy komponentlar

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Toast success | notification | `toast_success` |
| Toast error | notification | `toast_error` |
| Dropdown option (umumiy) | option | `dropdown_option_${value}` |
| Validation error xabar | text | `validation_error_${field}` |

---

### 24. Landing sahifa (`/`)

| Element | Turi | `data-testid` nomi |
|---------|------|----------------|
| Sign In link/button | link | `landing_sign_in_button` |
| From input | input | `landing_from_input` |
| To input | input | `landing_to_input` |
| When button | button | `landing_when_button` |
| Search button | button | `landing_search_button` |

---

## Xulosa

- Jami: **~160+ element**
- Faqat `data-testid="nom"` qo'shiladi — boshqa hech narsa o'zgarmaydi
- Birinchi navbatda: **Login, Global/Header, Fleet, Loads, Trips** — bu joylar eng ko'p sinadi
- Hamma narsani birdan qilish shart emas — sahifa-sahifa qo'shsa ham bo'ladi
- Savol bo'lsa — QA jamoasiga yozing
