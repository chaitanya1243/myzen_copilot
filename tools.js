import {
  McpServer,
  ResourceTemplate,
} from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fetch from "node-fetch";

// Create an MCP server
const server = new McpServer({
  name: "Demo",
  version: "1.0.0",
});

server.tool(
  "searchServices",
  "Search for services by name or tag",
  {
    searchValue: z.string(),
  },
  async ({ searchValue }) => {
    try {
      const encodedSearchValue = encodeURIComponent(searchValue);
      // Make the URL without centerId so it searches across all centers
      const url = `https://qaapi.zenotibeta.com/api/services/search?SearchValue=${encodedSearchValue}&CenterId=08b5ff61-9cd4-49f8-9ed7-978b52161e89&TherapistId=712ab585-f0a3-4d6a-9f9f-8fa9450464d9&BookingSource=2&page=1&size=10&AppointmentDate=2025-04-25&CouplesService=false&UserId=305e55e4-9e0c-4232-b5e4-2b5c120ec0a2&iVariants=1&skipAddons=true&IncludeSegments=false&ApplyGuestPriceAdjustment=false&displayFreqServicesOnTop=true&skipServicePrerequisites=true&filterAmenity=0`;

      console.log(url);
      const response = await fetch(url, {
        method: "GET",
        headers: {
          Authorization: `Bearer AN:qa|$ARD#VC/YiuDVUVUOLmYdWyQ7YwrN7NMHgRYgMYOIICW3wu3ISsgNC84EFyfLxii9HXVXO4JjjXHdJkYeNIGSU63e7KnJRYn3HWeCCYX4h6Kd19wPCK19xLBIu0V6s1DxByMfKMT9mICDKTwrRCrbGORhFI1Qx3ay+9MhMa3MtcTP0gq821C3j9+JGlEe5Q9g0r8NLYmJYEWKBrHGWoIri8UCK3cIEpEO6QMtIQ634mMRJi30oEfMUqb/idjaDcQjbeht5hVB1Q7MFDuaBcbz1bFcqnGpXDgMpXQs8ozr5QFOyo6JL+6SFf3oaCwKH1flsxGTgHB6IEGGcOe6QrwMYNem8uGBbW98X3miRCM=`,
        },
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data = await response.json();

      // Check if the response has a Services array structure
      if (data && data.Services && Array.isArray(data.Services)) {
        // Extract relevant massage service information
        const massageServices = data.Services.map((service) => ({
          Id: service.Id,
          Name: service.Name,
          CategoryName: service.CategoryName,
          Duration: service.Duration,
          Price: service.Price ? service.Price.Final : 0,
          Description: service.Description,
        }));

        // Limit to 10 results
        const limitedResults = massageServices.slice(0, 10);

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  searchTerm: searchValue,
                  totalFound: data.TotalServices || data.Services.length,
                  results: data.Services,
                },
                null,
                2
              ),
            },
          ],
        };
      } else {
        // If the expected structure is not found, return the raw data
        return {
          content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error searching for services: ${error.message}`,
          },
        ],
      };
    }
  }
);

// Add tool to get available appointment slots
server.tool(
  "getAvailableSlots",
  "Get available appointment slots at a center for a specific date and service and then summarize the slots so that it's easy to understand. Make it concise, should not exceed 10 lines, and don't mention the service again",
  {
    centerDate: z.string(),
  },
  async ({ centerDate }) => {
    try {
      const url = `https://qaapi.zenotibeta.com/api/v3.0/appointments/availabletimes`;

      const centerId = "08b5ff61-9cd4-49f8-9ed7-978b52161e89";
      const payload = {
        CouplesService: false,
        CenterId: "08b5ff61-9cd4-49f8-9ed7-978b52161e89",
        CenterDate: centerDate,
        ReservationId: null,
        SlotBookings: [
          {
            GuestId: "c25f1a80-cfbb-11ed-9570-89534ca1e8f3",
            VirtualGuest: {
              FirstName: null,
              LastName: null,
              Mobile: null,
              Gender: null,
            },
            AppointmentGroupId: null,
            waitlist_group_id: null,
            quote_pk: null,
            RemoveBuddyServiceFinishSegment: true,
            SkipAutoOrderingOfServices: false,
            email_link: null,
            sms_link: null,
            appointment_category_id: null,
            waitlist_id: null,
            SlotBookingIdentifier: "appointment_1",
            TherapistId: "712ab585-f0a3-4d6a-9f9f-8fa9450464d9",
            BookingNotes: "",
            PreferredTime: null,
            Price: null,
            ConsiderSingleTherapistSlot: true,
            Services: [],
          },
        ],
        IsNoncontiguousSlots: false,
        CheckFutureDayAvailability: true,
        TherapistDoubleBooking: null,
        OverrideAppCreationInNonScheduledHours: true,
        OverrideAllowAppointmentOverlap: null,
        ConsiderOnlyCheckedInEmployees: false,
        BookingSource: 2,
        FilterPastSlots: false,
        IsQueueMode: false,
        WaitlistGroupId: null,
        CheckDoubleBookingForAllSlots: false,
        CheckOnlyIfSlotExists: false,
        RequestGuidForSlots: "28c8f793-b1b4-42ce-b488-1500eb789afe",
      };

      const response = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer AN:qa|$ARD#VC/YiuDVUVUOLmYdWyQ7YwrN7NMHgRYgMYOIICW3wu3ISsgNC84EFyfLxii9HXVXO4JjjXHdJkYeNIGSU63e7KnJRYn3HWeCCYX4h6Kd19wPCK19xLBIu0V6s1DxByMfKMT9mICDKTwrRCrbGORhFI1Qx3ay+9MhMa3MtcTP0gq821C3j9+JGlEe5Q9g0r8NLYmJYEWKBrHGWoIri8UCK3cIEpEO6QMtIQ634mMRJi30oEfMUqb/idjaDcQjbeht5hVB1Q7MFDuaBcbz1bFcqnGpXDgMpXQs8ozr5QFOyo6JL+6SFf3oaCwKH1flsxGTgHB6IEGGcOe6QrwMYNem8uGBbW98X3miRCM=`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data = await response.json();

      // Process and format the response
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                availableSlots: data,
              },
              null,
              2
            ),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error fetching available slots: ${error.message}`,
          },
        ],
      };
    }
  }
);

// Add tool to search for guests
server.tool(
  "searchGuests",
  "Search for guests by name or other criteria",
  {
    searchValue: z.string(),
  },
  async ({ searchValue }) => {
    try {
      const encodedSearchValue = encodeURIComponent(searchValue);
      const url = `https://qaapi.zenotibeta.com/api/guests/search/?SearchValue=${encodedSearchValue}&prioritizeBaseCenterResults=true&CenterId=null`;

      const response = await fetch(url, {
        method: "GET",
        headers: {
          Authorization: `Bearer AN:qa|$ARD#VC/YiuDVUVUOLmYdWyQ7YwrN7NMHgRYgMYOIICW3wu3ISsgNC84EFyfLxii9HXVXO4JjjXHdJkYeNIGSU63e7KnJRYn3HWeCCYX4h6Kd19wPCK19xLBIu0V6s1DxByMfKMT9mICDKTwrRCrbGORhFI1Qx3ay+9MhMa3MtcTP0gq821C3j9+JGlEe5Q9g0r8NLYmJYEWKBrHGWoIri8UCK3cIEpEO6QMtIQ634mMRJi30oEfMUqb/idjaDcQjbeht5hVB1Q7MFDuaBcbz1bFcqnGpXDgMpXQs8ozr5QFOyo6JL+6SFf3oaCwKH1flsxGTgHB6IEGGcOe6QrwMYNem8uGBbW98X3miRCM=`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data = await response.json();

      // Check if the response has a Guests array structure
      if (data && data.Guests && Array.isArray(data.Guests)) {
        // Store the full guest data for context
        const fullGuestData = data.Guests;

        // Extract relevant guest information
        const guestSummaries = data.Guests.map((guest) => ({
          Id: guest.Id,
          Code: guest.Code,
          FullName: `${guest.FirstName || ""} ${guest.LastName || ""}`.trim(),
          Email: guest.Email || "Not provided",
          PhoneNumber:
            guest.MobileNumber ||
            (guest.MobilePhoneModel && guest.MobilePhoneModel.Number) ||
            "Not provided",
          Gender:
            guest.Gender === 1
              ? "Male"
              : guest.Gender === 2
              ? "Female"
              : "Not specified",
          Center: guest.CenterName,
        }));

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  searchTerm: searchValue,
                  totalFound: data.Total || data.Guests.length,
                  results: guestSummaries,
                  fullGuestData: fullGuestData, // Include full data for context
                },
                null,
                2
              ),
            },
          ],
        };
      } else {
        // If the expected structure is not found, return the raw data
        return {
          content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error searching for guests: ${error.message}`,
          },
        ],
      };
    }
  }
);

// Add tool to create a new guest
server.tool(
  "createGuest",
  "Create a new guest with the provided details",
  {
    firstName: z.string(),
    lastName: z.string(),
    username: z.string(),
    email: z.string().email(),
    phoneNumber: z.string().optional(),
    gender: z.number().min(0).max(2).optional().default(0), // 0: Not specified, 1: Male, 2: Female
    dateOfBirth: z.string().optional(),
  },
  async ({
    firstName,
    lastName,
    username,
    email,
    phoneNumber,
    gender,
    dateOfBirth,
  }) => {
    try {
      const url = `https://qaapi.zenotibeta.com/api/Guests/Add`;

      // Create mobile phone model if phone number is provided
      let mobilePhoneModel = null;
      if (phoneNumber) {
        mobilePhoneModel = {
          Number: phoneNumber,
          DisplayNumber: phoneNumber,
        };
      }

      // Create request payload
      const payload = {
        CenterId: "08b5ff61-9cd4-49f8-9ed7-978b52161e89",
        Guest: {
          Id: null,
          FirstName: firstName,
          LastName: lastName,
          Code: null,
          Username: username,
          PostalCode: null,
          Address1: null,
          City: null,
          State: null,
          Country: null,
          DOB_IncompleteYear: null,
          DateOfBirth: dateOfBirth || null,
          IsMinors: dateOfBirth
            ? new Date(dateOfBirth) >
              new Date(new Date().setFullYear(new Date().getFullYear() - 18))
            : false,
          AnniversaryDate: null,
          Email: email,
          Room: null,
          Gender: gender,
          MobileNumber: phoneNumber || null,
          MobilePhoneModel: mobilePhoneModel,
          WorkPhone: null,
          WorkPhoneModel: null,
          HomePhone: null,
          HomePhoneModel: null,
          RelationshipManager: null,
          Nationality: null,
          ReferralSource: null,
          ReferredGuestId: null,
          ReceiveMarketingSMS: false,
          ReceiveTransactionalSMS: true,
          ReceiveTransactionalEmail: true,
          ReceiveMarketingEmail: false,
          ReceiveLPStmt: true,
          OptInForLoyaltyProgram: true,
          PreferredPronounId: null,
          PreferredPronoun: null,
          GuestMarketingLoyaltyOptIn: false,
        },
        Validate: true,
      };

      const response = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer AN:qa|$ARD#VC/YiuDVUVUOLmYdWyQ7YwrN7NMHgRYgMYOIICW3wu3ISsgNC84EFyfLxii9HXVXO4JjjXHdJkYeNIGSU63e7KnJRYn3HWeCCYX4h6Kd19wPCK19xLBIu0V6s1DxByMfKMT9mICDKTwrRCrbGORhFI1Qx3ay+9MhMa3MtcTP0gq821C3j9+JGlEe5Q9g0r8NLYmJYEWKBrHGWoIri8UCK3cIEpEO6QMtIQ634mMRJi30oEfMUqb/idjaDcQjbeht5hVB1Q7MFDuaBcbz1bFcqnGpXDgMpXQs8ozr5QFOyo6JL+6SFf3oaCwKH1flsxGTgHB6IEGGcOe6QrwMYNem8uGBbW98X3miRCM=`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (data.Error) {
        throw new Error(`API error: ${data.Error}`);
      }

      // Save guest information for future reference
      const createdGuest = {
        guestId: data.GuestId,
        firstName,
        lastName,
        email,
        phoneNumber,
        username,
        gender:
          gender === 1 ? "Male" : gender === 2 ? "Female" : "Not specified",
        dateOfBirth,
      };

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                success: true,
                message: `Guest ${firstName} ${lastName} created successfully`,
                guestDetails: createdGuest,
                apiResponse: data,
              },
              null,
              2
            ),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          { type: "text", text: `Error creating guest: ${error.message}` },
        ],
      };
    }
  }
);

// Add tool to get guest creation mandatory fields
server.tool(
  "getGuestMandatoryFields",
  "Get the mandatory fields required for guest creation from the organization settings",
  {},
  async () => {
    try {
      const url = `https://qaapi.zenotibeta.com/v1/organizations/settings/all`;

      const response = await fetch(url, {
        method: "GET",
        headers: {
          Authorization: `Bearer AN:qa|$ARD#VC/YiuDVUVUOLmYdWyQ7YwrN7NMHgRYgMYOIICW3wu3ISsgNC84EFyfLxii9HXVXO4JjjXHdJkYeNIGSU63e7KnJRYn3HWeCCYX4h6Kd19wPCK19xLBIu0V6s1DxByMfKMT9mICDKTwrRCrbGORhFI1Qx3ay+9MhMa3MtcTP0gq821C3j9+JGlEe5Q9g0r8NLYmJYEWKBrHGWoIri8UCK3cIEpEO6QMtIQ634mMRJi30oEfMUqb/idjaDcQjbeht5hVB1Q7MFDuaBcbz1bFcqnGpXDgMpXQs8ozr5QFOyo6JL+6SFf3oaCwKH1flsxGTgHB6IEGGcOe6QrwMYNem8uGBbW98X3miRCM=`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data = await response.json();

      // Extract guest mandatory fields
      let mandatoryFields = [];
      let isMobileRequired = false;
      let otherSettings = {};

      if (data && data.guest) {
        // Get mandatory fields array
        if (
          data.guest.guest_manadatory_fields &&
          Array.isArray(data.guest.guest_manadatory_fields)
        ) {
          mandatoryFields = data.guest.guest_manadatory_fields;
        }

        // Check if mobile number is mandatory
        if (data.guest.is_mobile_number_mandatory !== undefined) {
          isMobileRequired = data.guest.is_mobile_number_mandatory;
        }

        // Get other relevant guest settings
        otherSettings = {
          enforceMandatoryFields: data.guest.enforce_guest_fields || false,
          checkMinorAge: data.guest.Check_Minor_Age || false,
          minorAge: data.guest.Minor_Age || 18,
          allowSameEmail:
            data.guest.Allow_Guest_With_Same_Email_Address || false,
          allowSameMobile: data.guest.Allow_Guest_With_Same_Mobile || false,
          enableOtherGender: data.guest.Enable_Other_Gender || false,
        };
      }

      // Format the fields in a more human-readable way
      const formattedFields = mandatoryFields.map((field) => {
        switch (field) {
          case "dob":
            return "Date of Birth";
          case "email":
            return "Email";
          case "gender":
            return "Gender";
          case "mobile":
            return "Mobile Number";
          case "username":
            return "Username";
          default:
            return field.charAt(0).toUpperCase() + field.slice(1); // Capitalize the field name
        }
      });

      if (isMobileRequired && !formattedFields.includes("Mobile Number")) {
        formattedFields.push("Mobile Number");
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                mandatoryFields: formattedFields,
                rawMandatoryFields: mandatoryFields,
                isMobileRequired,
                otherSettings,
              },
              null,
              2
            ),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error fetching mandatory fields: ${error.message}`,
          },
        ],
      };
    }
  }
);

// Add a dynamic greeting resource

// Add tool to reserve slots for a service
server.tool(
  "reserveServiceSlot",
  "Reserve a slot for a service appointment",
  {
    guestId: z.string(),
    centerId: z.string(),
    slotTime: z.string()
  },
  async ({ guestId, slotTime, centerId }) => {
    try {
      const url = `https://qaapi.zenotibeta.com/api/v2.0/Appointments/ReserveSlots`;

      // Default center ID
      const centerId = "08b5ff61-9cd4-49f8-9ed7-978b52161e89";
      const serviceObject = {}
      // Default therapist if not provided
      const defaultTherapistId =
        therapistId || "712ab585-f0a3-4d6a-9f9f-8fa9450464d9";

      // // Extract the date part from startTime if centerDate is not provided
      // const centerTimeValue = centerDate || startTime.split('T')[0] + ' ' + startTime.split('T')[1];

      // Create full payload
      const payload = {
        CouplesService: false,
        CenterId: centerId,
        ReservationId: null,
        SlotBookings: [
          {
            GuestId: guestId,
            VirtualGuest: {
              FirstName: null,
              LastName: null,
              Mobile: null,
              Gender: null,
            },
            AppointmentGroupId: null,
            waitlist_group_id: null,
            quote_pk: null,
            RemoveBuddyServiceFinishSegment: true,
            SkipAutoOrderingOfServices: false,
            email_link: null,
            sms_link: null,
            appointment_category_id: null,
            waitlist_id: null,
            SlotBookingIdentifier: "appointment_1",
            TherapistId: null,
            BookingNotes: "",
            PreferredTime: null,
            Price: null,
            ConsiderSingleTherapistSlot: true,
            Services: [
              {
                OrderNo: 2,
                CoupleGroupNo: 1,
                CoupleGroupId: null,
                AppointmentId: null,
                InvoiceItemId: null,
                UIItemIdentifier: "appointment_1#item_2",
                CartItemId: null,
                Lock: false,
                PackageId: null,
                PkgGroupNo: null,
                Service: serviceObject,
                ResetIfTherapistCanNotDoService: false,
                StartTime: slotTime,
                StartTimeInCenter: null,
                EndTime: null,
                EndTimeInCenter: null,
                RequestedDuration: null,
                RequestedTherapistGender: 3,
                RequestedTherapist: {
                  Id: "712ab585-f0a3-4d6a-9f9f-8fa9450464d9",
                  ShortName: null,
                  NickName: null,
                  FullName: "Patty Edinburg",
                  Email: null,
                  PhoneNumber: null,
                  MobilePhoneModel: null,
                  Gender: 2,
                  FirstName: "Patty",
                  LastName: "Edinburg",
                  IsAvailable: true,
                  WaiveBiometricFlag: false,
                  VanityImageUrl: null,
                  ScalingFactor: 0,
                  ScaledPrice: 0,
                  ServiceTime: 0,
                  DisplayName: null,
                  PreferredPronoun: null,
                  IdleTime: null,
                  OriginalPrice: 0,
                  OriginalTax: 0,
                  Job: {
                    indicator_color: "#F8FF2E",
                    id: "fc9e78b2-10b2-4a4b-b69c-0f8605181c23",
                    name: "MANAGER",
                  },
                  Tags: null,
                  BookingInterval: 0,
                  sort_order: 3,
                  schedule_order: 99999999,
                  booking_value_order: -1,
                  schedule: null,
                  unavailable_times: null,
                  LastDate: null,
                  IsGuestSpecificDuration: false,
                  IsGuestSpecificPrice: false,
                  IsOnlyGender: false,
                },
                RequestedParallelGroupFk: null,
                Room: null,
                Equipment: null,
                AssignDefaultSlot: true,
                FillOpenSlots: false,
                AppointmentSource: 0,
                Do_Not_Reprocess_Therapist: true,
                IsGuestSpecificDuration: false,
                isGuestSpecificPriceUpdated: false,
                QuoteItemPk: null,
                is_flexi_day_package: false,
                is_service_bundle_day_package: false,
                service_bundle_day_package_id: null,
                service_bundle_day_package_group_no: null,
                service_bundle_package_no: 1,
              },
            ],
          },
        ],
        CenterTime: "2025-05-26 19:15:00",
        BookingSource: 2,
        IsNoncontiguousSlots: false,
        ConsiderOnlyCheckedInEmployees: false,
        WaitlistGroupId: null,
      };

      const response = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer AN:qa|$ARD#VC/YiuDVUVUOLmYdWyQ7YwrN7NMHgRYgMYOIICW3wu3ISsgNC84EFyfLxii9HXVXO4JjjXHdJkYeNIGSU63e7KnJRYn3HWeCCYX4h6Kd19wPCK19xLBIu0V6s1DxByMfKMT9mICDKTwrRCrbGORhFI1Qx3ay+9MhMa3MtcTP0gq821C3j9+JGlEe5Q9g0r8NLYmJYEWKBrHGWoIri8UCK3cIEpEO6QMtIQ634mMRJi30oEfMUqb/idjaDcQjbeht5hVB1Q7MFDuaBcbz1bFcqnGpXDgMpXQs8ozr5QFOyo6JL+6SFf3oaCwKH1flsxGTgHB6IEGGcOe6QrwMYNem8uGBbW98X3miRCM=`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data = await response.json();

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(data, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error reserving service slot: ${error.message}`,
          },
        ],
      };
    }
  }
);

// Start receiving messages on stdin and sending messages on stdout
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main();
