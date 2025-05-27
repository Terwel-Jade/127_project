import customtkinter as ctk
import mysql.connector
from tkinter import messagebox
from db import StudentOrgDBMS
from tkcalendar import DateEntry

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.db = StudentOrgDBMS()

        self.title("Student Organization")
        self.geometry("900x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.resizable(False, False)

        self.current_frame = None
        self.show_frame(SelectScreen)

    def show_frame(self, frame_class, *args):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, *args)
        self.current_frame.pack(expand=True, fill="both")


class SelectScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self, text="Welcome!", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)
        ctk.CTkLabel(self, text="Please choose whether you are a member or admin.",
                     font=ctk.CTkFont(size=18)).pack(pady=30)

        ctk.CTkButton(self, text="Member", command=lambda: master.show_frame(EnterAsMember)).pack(pady=10)
        ctk.CTkButton(self, text="Administrator", command=lambda: master.show_frame(EnterAsAdmin)).pack(pady=10)


class EnterAsMember(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.db = StudentOrgDBMS()

        ctk.CTkLabel(self, text="Member Dashboard", font=ctk.CTkFont(size=20)).pack(pady=20)
        ctk.CTkButton(self, text="Go Back", command=lambda: master.show_frame(SelectScreen)).pack(pady=10)

        self._form_one()

    def _form_one(self):
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        ctk.CTkButton(self, text='Sign In', command=self.sign_in).pack(pady=10)
        
        ctk.CTkLabel(self, text="Have no account yet?", font=ctk.CTkFont(size=10)).pack(pady=2)
        ctk.CTkButton(self, text="Sign Up", command=lambda: self.master.show_frame(AddMemberStudent)).pack(pady=2)
    
    def _get_credentials(self):
        return self.username_entry.get().strip(), self.password_entry.get().strip()

    def sign_in(self):
        username, password = self._get_credentials()
        # Check if username and password empty, return error message
        if not username or not password:
            messagebox.showerror("Error", "Please fill up the form.")
            return
        
        checkpassword = self.db.checkUsernamePassword(username, "Member")

        if checkpassword and checkpassword[0] == password:
            #messagebox.showinfo("Successfully log in!", "Ayos")
            self.master.show_frame(MemberScreen, username)
        else:
            messagebox.showerror("Failed", "Invalid username or password.")

class AddMemberStudent(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.db = StudentOrgDBMS()

        ctk.CTkButton(self, text="Go Back", command=lambda: master.show_frame(EnterAsMember)).pack(pady=10)
        ctk.CTkLabel(self, text="Please fill up the form", font=ctk.CTkFont(size=20)).pack(pady=20)

        self._form_two()
        ctk.CTkButton(self, text="Submit", command=self.handle_addMembership).pack(pady=10)

    def _form_two(self):
        self.stud_num_entry = ctk.CTkEntry(self, placeholder_text="Student Number")
        self.stud_num_entry.pack(pady=10)

        self.fname_entry = ctk.CTkEntry(self, placeholder_text="First Name")
        self.fname_entry.pack(pady=10)

        self.lname_entry = ctk.CTkEntry(self, placeholder_text="Last Name")
        self.lname_entry.pack(pady=10)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        self.gender_entry = ctk.CTkOptionMenu(self, values=["M", "F", "X"])
        self.gender_entry.pack(pady=10)

        self.acad_yr_entry = ctk.CTkEntry(self, placeholder_text="Academic Year Enrolled")
        self.acad_yr_entry.pack(pady=10)

        self.deg_prog_entry = ctk.CTkEntry(self, placeholder_text="Degree Program (ex: BSSTAT, BSCS)")
        self.deg_prog_entry.pack(pady=10)

    def handle_addMembership(self):
        self.addMember()
        self.master.show_frame(MemberScreen, self.username_entry.get().strip())

    def addMember(self):
        student_num = self.stud_num_entry.get().strip()
        first_name = self.fname_entry.get().strip()
        last_name = self.lname_entry.get().strip()
        mem_username = self.username_entry.get().strip()
        mem_password = self.password_entry.get().strip()
        gender = self.gender_entry.get()
        acad_year_enrolled = self.acad_yr_entry.get().strip()
        degree_prog = self.deg_prog_entry.get().strip()
        self.db.add_student(student_num, first_name, last_name, mem_username, mem_password, gender, acad_year_enrolled, degree_prog)

class MemberScreen(ctk.CTkFrame):
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username

        self.db = StudentOrgDBMS()

        # Access the information of the student
        student_num = self.db.get_stud_num(self.username)
        first_name, last_name = self.db.get_stud_name(student_num[0])

        ctk.CTkLabel(self, text=f"Hello, {first_name}!", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        ctk.CTkButton(self, text="Sign out", command=lambda: master.show_frame(SelectScreen)).pack(pady=10)

        tab_view = ctk.CTkTabview(self, width=900, height=600)
        tab_view.pack(pady=10)

        tab_view.add("Home")
        tab_view.add("Organizations")
        tab_view.add("Payments")
        tab_view.add("Profile")

        home_tab = tab_view.tab("Home")
        org_tab = tab_view.tab("Organizations")
        pay_tab = tab_view.tab("Payments")
        profile_tab = tab_view.tab("Profile")

        self.build_home(home_tab)
        self.build_profile_tab(profile_tab, first_name, last_name, student_num[0])
        self.build_org_tab(org_tab, student_num[0])
        self.build_pay_tab(pay_tab, student_num[0])

    def build_home(self, parent):
        ctk.CTkLabel(parent, text="Welcome to the database!", font=ctk.CTkFont(size=14, weight="normal")).pack(pady=10)

    def build_org_tab(self, parent, student_num):
        orgs = self.db.check_if_have_org(student_num)

        if orgs:
            scroll_frame = ctk.CTkScrollableFrame(parent, width=600, height=300)
            scroll_frame.pack(pady=10)

            for org_name, status in orgs:
                ctk.CTkLabel(
                    scroll_frame,
                    text=f"{org_name}   |   Status: {status}"
                ).pack(anchor="w", padx=10, pady=5)
        else:
            ctk.CTkLabel(parent, text="You have not yet joined any org", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        #ctk.CTkButton(parent, text="Join Org", command=lambda: self.master.show_frame(JoinOrg, student_num)).pack(pady=10)

    def build_profile_tab(self, parent, first_name, last_name, student_num):
        ctk.CTkLabel(parent, text=f"{first_name} {last_name}", font=ctk.CTkFont(size=14, weight="normal")).pack(pady=10)
        ctk.CTkButton(parent, text="Edit Credentials", command=lambda: self.master.show_frame(EditStudent, self.username, student_num)).pack(pady=10)

    def build_pay_tab(self, parent, student_num):
        pays = self.db.get_all_payments(student_num)

        if pays:
            scroll_frame = ctk.CTkScrollableFrame(parent, width=800, height=600)
            scroll_frame.pack(pady=10)

            for trans_num, status, date, amount, due, org in pays:
                if date:
                    ctk.CTkLabel(scroll_frame, text=f"You have a transaction with {org} (Transaction #{trans_num}) for an amount of {amount}, \nwhich is currently {status}, made on {date} and due on {due}.").pack(anchor="w", padx=10, pady=5)
                else:
                    ctk.CTkLabel(scroll_frame, text=f"You have a transaction with {org} (Transaction #{trans_num}) for an amount of {amount}, \nwhich is currently {status} and is due on {due}.").pack(anchor="w", padx=10, pady=5)
        else:
            ctk.CTkLabel(parent, text="You have no transactions", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

class EditStudent(ctk.CTkFrame):
    def __init__(self, master, username, student_num):
        super().__init__(master)
        self.username = username
        self.student_num = student_num
        
        self.db = StudentOrgDBMS()

        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(MemberScreen, self.username)).pack(pady=10) # Go back
        ctk.CTkLabel(self, text="Edit My Credentials", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        self.editFormStudent()
        ctk.CTkButton(self, text="Submit", command=lambda: self.handleEditButton).pack(pady=10)

    def editFormStudent(self):
        self.edit_username = ctk.CTkEntry(self, placeholder_text="New username")
        self.edit_username.pack(pady=10)

        self.edit_oldpassword = ctk.CTkEntry(self, placeholder_text="Old password")
        self.edit_oldpassword.pack(pady=10)

        self.edit_newpassword = ctk.CTkEntry(self, placeholder_text="New password")
        self.edit_newpassword.pack(pady=10)

    def handleEditButton(self):
        old_password_entry = self.edit_oldpassword.get().strip()
        username = self.edit_username.get().strip()
        password = self.edit_newpassword.get().strip()

        old_setPasswrod = self.db.checkOldPassword(self.student_num)
        if old_setPasswrod and old_setPasswrod[0] == old_password_entry:
            self.db.update_member(username, password, self.student_num)

            messagebox.showinfo("Successful", "Successfully changed informations")
            self.master.show_frame(MemberScreen, self.username)
        else:
            messagebox.showerror("Failed", "Incorrect old password")
            return

class JoinOrg(ctk.CTkFrame):
    def __init__(self, master, student_num):
        super().__init__(master)
        self.student_num = student_num

        self.db = StudentOrgDBMS()

        self.username = self.db.get_username(student_num)[0]

        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(MemberScreen, self.username)).pack(pady=10) # Go back

        self.formthree()
        ctk.CTkButton(self, text="Join", command=self.handle_joining).pack(pady=10)

    def formthree(self):
        self.join_org_name = ctk.CTkEntry(self, placeholder_text="Organization Name")
        self.join_org_name.pack(pady=10)

        #self.org_id = self.db.get_org_id(self.join_org_name.get().strip())

        self.join_acad_year = ctk.CTkEntry(self, placeholder_text="Academic Year")
        self.join_acad_year.pack(pady=10)

        self.join_sem = ctk.CTkOptionMenu(self, values=["1", "2", "M"])
        self.join_sem.pack(pady=10)

        # When a student joins, membership status is default to active,classification is default to 'resident', type is NULL, role is NULL
       #print(self.org_id)

    def handle_joining(self):
        org_name = self.join_org_name.get().strip()
        org_id_tuple = self.db.get_org_id(org_name)

        if not org_id_tuple:
            messagebox.showerror("Failed", "Invalid organization")
            return

        self.org_id = org_id_tuple[0]

        self.joinMember()
        self.master.show_frame(MemberScreen, self.username) # Go back

    def joinMember(self):
        academic_year = self.join_acad_year.get().strip()
        semester = self.join_sem.get()

        self.db.add_membership(self.student_num, self.org_id, "Active", academic_year, "Resident", None, None, semester)


#####################################################################

class EnterAsAdmin(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.db = StudentOrgDBMS()

        ctk.CTkLabel(self, text="Admin Dashboard", font=ctk.CTkFont(size=20)).pack(pady=20)
        ctk.CTkButton(self, text="Go Back", command=lambda: master.show_frame(SelectScreen)).pack(pady=10)

        self._form_one()

    def _form_one(self):
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        ctk.CTkButton(self, text='Sign In', command=self.sign_in).pack(pady=10)
        
        ctk.CTkLabel(self, text="Have no account yet?", font=ctk.CTkFont(size=10)).pack(pady=2)
        ctk.CTkButton(self, text="Sign Up", command=lambda: self.master.show_frame(AddOrganization)).pack(pady=2)
    
    def _get_credentials(self):
        return self.username_entry.get().strip(), self.password_entry.get().strip()

    def sign_in(self):
        username, password = self._get_credentials()
        # Check if username and password empty, return error message
        if not username or not password:
            messagebox.showerror("Error", "Please fill up the form.")
            return
        
        checkpassword = self.db.checkUsernamePassword(username, "Organization")

        if checkpassword and checkpassword[0] == password:
            #messagebox.showinfo("Successfully log in!", "Ayos")
            self.master.show_frame(AdminScreen, username)
        else:
            messagebox.showerror("Failed", "Invalid username or password.")

class AddOrganization(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.db = StudentOrgDBMS()

        ctk.CTkButton(self, text="Go Back", command=lambda: master.show_frame(EnterAsAdmin)).pack(pady=10)
        ctk.CTkLabel(self, text="Please fill up the form", font=ctk.CTkFont(size=20)).pack(pady=20)

        self._form_two()
        ctk.CTkButton(self, text="Submit", command=self.handle_addOrg).pack(pady=10)

    def _form_two(self):
        self.org_id_entry = ctk.CTkEntry(self, placeholder_text="Organization ID")
        self.org_id_entry.pack(pady=10)

        self.org_name_entry = ctk.CTkEntry(self, placeholder_text="Organization Name")
        self.org_name_entry.pack(pady=10)

        self.org_year_founded_entry= ctk.CTkEntry(self, placeholder_text="Year Founded")
        self.org_year_founded_entry.pack(pady=10)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        self.org_type_entry = ctk.CTkOptionMenu(self, values=["University", "College", "GS", "NDMO", "University-wide", "N/A"])
        self.org_type_entry.pack(pady=10)

    def handle_addOrg(self):
        self.addOrg()
        self.master.show_frame(AdminScreen, self.username_entry.get().strip())

    def addOrg(self):
        org_id = self.org_id_entry.get().strip()
        org_username = self.username_entry.get().strip()
        org_password = self.password_entry.get().strip()
        org_name = self.org_name_entry.get().strip()
        year_founded = self.org_year_founded_entry.get().strip()
        org_type = self.org_type_entry.get()
        self.db.add_organization(org_id, org_username, org_password, org_name, year_founded, org_type)

class AdminScreen(ctk.CTkFrame):
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username

        self.db = StudentOrgDBMS()

        # Access the information of the student
        org_id = self.db.get_org_id_username(self.username)
        org_name = self.db.get_org_name(org_id[0])

        ctk.CTkLabel(self, text=f"Hello, {org_name[0]}!", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        ctk.CTkButton(self, text="Sign out", command=lambda: master.show_frame(SelectScreen)).pack(pady=10)

        tab_view = ctk.CTkTabview(self, width=900, height=600)
        tab_view.pack(pady=10)

        tab_view.add("Home")
        tab_view.add("Members")
        tab_view.add("Payments")
        tab_view.add("Events")
        tab_view.add("Reports")
        tab_view.add("Profile")

        home_tab = tab_view.tab("Home")
        org_tab = tab_view.tab("Members")
        pay_tab = tab_view.tab("Payments")
        events_tab = tab_view.tab("Events")
        report_tab = tab_view.tab("Reports")
        profile_tab = tab_view.tab("Profile")

        self.build_home(home_tab)
        self.build_mem_tab(org_tab, org_id[0])
        self.build_profile_tab(profile_tab, org_id[0], org_name[0])
        self.build_event_tab(events_tab, org_id[0])
        self.build_payment_tab(pay_tab, org_id[0], username)
        self.build_report_tab(report_tab, org_id[0])

    def build_home(self, parent):
        ctk.CTkLabel(parent, text="Welcome to the database!", font=ctk.CTkFont(size=14, weight="normal")).pack(pady=10)

    def build_report_tab(self, parent, org_id):
        ctk.CTkLabel(parent, text="Organization Reports", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(parent, width=800, height=400)
        self.scroll_frame.pack(pady=10)

        self.report_choice = ctk.CTkOptionMenu(self.scroll_frame, values=["Member Roles", "Member Status", "Member Gender", "Member Degree Program", "Batch (Year)", "Committee"])
        self.report_choice.pack(pady=10)

        #ctk.CTkLabel(scroll_frame, text="Members Role", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=10)
        ctk.CTkButton(self.scroll_frame, text="Generate", command=lambda: self.displayReport(org_id)).pack(pady=10)

        self.roles_display_frame = ctk.CTkFrame(self.scroll_frame)
        self.roles_display_frame.pack(pady=10, fill="both", expand=True)

        ## Second form for generating reports
        ctk.CTkLabel(self.scroll_frame, text="Other Reports", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        self.report_variant = ctk.CTkOptionMenu(self.scroll_frame, values=["Executive Committee", "President", "Vice President", "Secretary","Treasurer", "Head","% Active vs Inactive", "Alumni", "Highest Debt", "Late Payments", "Total Amount (Paid/Not Paid)", "Unpaid Transactions"], command=self.update_variant_inputs)
        self.report_variant.pack(pady=5)

        self.variant_input_frame = ctk.CTkFrame(self.scroll_frame)
        self.variant_input_frame.pack(pady=10, fill="both", expand=True)

        ctk.CTkButton(self.scroll_frame, text="Generate", command=lambda: self.displayReportTwo(org_id)).pack(pady=10)


        self.second_report_frame = ctk.CTkFrame(self.scroll_frame)
        self.second_report_frame.pack(pady=10, fill="both", expand=True)

        self.query_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="Enter query (remove ';')")
        self.query_entry.pack(padx=10, pady=10, fill="x")

        ctk.CTkButton(self.scroll_frame, text="Submit", command=self.showResults).pack(pady=10)

        self.third_report_frame = ctk.CTkFrame(self.scroll_frame)
        self.third_report_frame.pack(pady=10, fill="both", expand=True)

    def showResults(self):
        for widget in self.third_report_frame.winfo_children():
            widget.destroy()

        query = self.query_entry.get().strip()

        if not query:
            messagebox.showerror("Failed", "Query cannot be empty!")
            return
        
        try:
            results = self.db.enterQuery(query)

            for row in results:
                ctk.CTkLabel(self.third_report_frame, text=row).pack(anchor="w", padx=10)
        
        except Exception as e:
            messagebox.showerror("Failed", f"Error: {e}")

    def update_variant_inputs(self, variant):
        for widget in self.variant_input_frame.winfo_children():
            widget.destroy()

        if variant in ["Executive Committee", "Alumni", "Highest Debt", "Late Payments"]:
            self.textBox = ctk.CTkEntry(self.variant_input_frame, placeholder_text="Academic Year")
            self.textBox.pack(pady=10)

        if variant == "Unpaid Transactions":
            self.sem_debt = ctk.CTkOptionMenu(self.variant_input_frame, values=["1", "2", "M"])
            self.sem_debt.pack(pady=10)
            self.textBox = ctk.CTkEntry(self.variant_input_frame, placeholder_text="Academic Year")
            self.textBox.pack(pady=10)

        elif variant == "Total Amount (Paid/Not Paid)":
            ctk.CTkLabel(self.variant_input_frame, text="Date:", font=ctk.CTkFont(size=14)).pack(pady=10)
            self.fee_due_entry = DateEntry(self.variant_input_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            self.fee_due_entry.pack(pady=10)
            # ctk.CTkLabel(self.variant_input_frame, text="Choose semester", font=ctk.CTkFont(size=10)).pack(pady=10)
            # self.sem_debt = ctk.CTkOptionMenu(self.variant_input_frame, values=["1", "2", "M"])
            # self.sem_debt.pack(pady=10)

    def displayReportTwo(self, org_id):
        for widget in self.second_report_frame.winfo_children():
            widget.destroy()

        report_variant = self.report_variant.get()

        if report_variant == "Executive Committee":
            self.showExecs(org_id, self.textBox.get().strip())

        elif report_variant in ["President", "Vice President", "Secretary", "Treasurer", "Head  "]:
            self.showAnyRole(org_id, report_variant)

        elif report_variant == "% Active vs Inactive":
            self.showPercentageActiveInactive(org_id, self.textBox.get().strip())

        elif report_variant == "Alumni":
            self.showAllAlums(org_id, self.textBox.get().strip())

        elif report_variant == "Highest Debt":
            semester = self.sem_debt.get() if hasattr(self, 'sem_debt') else None
            self.showDebtMem(org_id, self.textBox.get().strip(), semester)

        elif report_variant == "Late Payments":
            # semester = self.sem_debt.get() if hasattr(self, 'sem_debt') else None
            self.showLatePayments(org_id, self.textBox.get().strip(), semester)

        elif report_variant == "Total Amount (Paid/Not Paid)":
            date = self.fee_due_entry.get()
            self.showTotalTransactions(org_id, date)

        elif report_variant == "Unpaid Transactions":
            semester = self.sem_debt.get()
            acad_year = self.textBox.get().strip()
            self.showMemWithUnpaid(org_id, semester, acad_year)

    def showTotalTransactions(self, org_id, date):
        roles = self.db.totalTransactions(org_id, date)
        if roles:
            for status, total_amount in roles:
                member = ctk.CTkLabel(self.second_report_frame, text=f"{status} - PHP{total_amount}, as of {date}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.second_report_frame, text="No executive committee data", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)


    def showExecs(self, org_id, acad_year):
        roles = self.db.showExecs(org_id, acad_year)
        if roles:
            for fname, lname, role in roles:
                member = ctk.CTkLabel(self.second_report_frame, text=f"{fname} {lname}  -  {role}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.second_report_frame, text="No executive committee data", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

    def showAnyRole(self, org_id, role):
        roles = self.db.showAnyRoleInReverse(org_id, role)
        if roles:
            for fname, lname, role, acad_year in roles:
                member = ctk.CTkLabel(self.second_report_frame, text=f"{fname} {lname}  -  {acad_year}  |  {role}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.second_report_frame, text="No data", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

    def showLatePayments(self, org_id, academic_year, semester):
        roles = self.db.showLatePayments(org_id, academic_year, semester)
        if roles:
            for fname, lname, trans_num, date, due in roles:
                member = ctk.CTkLabel(self.second_report_frame, text=f"{fname} {lname}  -  Transaction #{trans_num} Date: {date}    Due: {due}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.second_report_frame, text="No data", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

    def showPercentageActiveInactive(self, org_id, n):
        roles = self.db.showPercentageofMems(org_id, n)
        if roles:
            for status, count, percentage in roles:
                member = ctk.CTkLabel(self.second_report_frame, text=f"Status: {status}  -  Count: {count}  -  %: {percentage}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.second_report_frame, text="No executive committee data", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

    def showAllAlums(self, org_id, year):
        roles = self.db.showAllAlumDate(org_id, year)
        if roles:
            for fname, lname, acad_year in roles:
                member = ctk.CTkLabel(self.second_report_frame, text=f"{fname} {lname}  -  {acad_year}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.second_report_frame, text="No data", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

    def showDebtMem(self, org_id, year, semester):
        roles = self.db.showDebtMem(org_id, None, None)
        if roles:
            for fname, lname, total_debt in roles:
                member = ctk.CTkLabel(self.second_report_frame, text=f"{fname} {lname}  -  Debt: {total_debt}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.second_report_frame, text="No data", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

    def showMemWithUnpaid(self, org_id, semester, year):
        roles = self.db.showUnpaidMem(org_id, semester , year)
        if roles:
            for fname, lname, trans_num, amount, due in roles:
                member = ctk.CTkLabel(self.second_report_frame, text=f"{fname} {lname} - Transaction #{trans_num} : Amount Php{amount}   Due in {due}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.second_report_frame, text="No data", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

    def displayReport(self, org_id):
        # Clears the generated scrollable
        for widget in self.roles_display_frame.winfo_children():
            #if isinstance(widget, ctk.CTkScrollableFrame):
            widget.destroy()

        report_type = self.report_choice.get()

        if report_type == "Member Roles":
            self.show_roles(org_id)
        elif report_type == "Member Status":
            self.show_status(org_id)
        elif report_type == "Member Gender":
            self.show_gender(org_id)
        elif report_type == "Member Degree Program":
            self.show_degree_program(org_id)
        elif report_type == "Batch (Year)":
            self.show_batches(org_id)
        elif report_type == "Committee":
            self.show_committees(org_id)

        
    def show_roles(self, org_id):
        roles = self.db.showRoles(org_id)
        if roles:
            for fname, lname, role in roles:
                member = ctk.CTkLabel(self.roles_display_frame, text=f"{fname} {lname}  -  {role}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.roles_display_frame, text="No member with role yet", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

    def show_status(self, org_id):
        roles = self.db.showStatus(org_id)
        if roles:
            for fname, lname, role in roles:
                member = ctk.CTkLabel(self.roles_display_frame, text=f"{fname} {lname}  -  {role}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.roles_display_frame, text="No member", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

    def show_gender(self, org_id):
        roles = self.db.showGender(org_id)
        if roles:
            for fname, lname, role in roles:
                member = ctk.CTkLabel(self.roles_display_frame, text=f"{fname} {lname}  -  {role}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.roles_display_frame, text="No member", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

    def show_degree_program(self, org_id):
        roles = self.db.showDegProg(org_id)
        if roles:
            for fname, lname, role in roles:
                member = ctk.CTkLabel(self.roles_display_frame, text=f"{fname} {lname}  -  {role}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.roles_display_frame, text="No member", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

    def show_batches(self, org_id):
        roles = self.db.showBatch(org_id)
        if roles:
            for fname, lname, role in roles:
                member = ctk.CTkLabel(self.roles_display_frame, text=f"{fname} {lname}  -  {role}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.roles_display_frame, text="No member", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

    def show_committees(self, org_id):
        roles = self.db.showCommittee(org_id)
        if roles:
            for fname, lname, role in roles:
                member = ctk.CTkLabel(self.roles_display_frame, text=f"{fname} {lname}  -  {role}")
                member.pack(pady=5)
        else:
            ctk.CTkLabel(self.roles_display_frame, text="No member", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)


    def build_mem_tab(self, parent, org_id):
        mems = self.db.get_memberships(org_id)

        if mems:
            scroll_frame = ctk.CTkScrollableFrame(parent, width=600, height=300)
            scroll_frame.pack(pady=10)

            for mem in mems:
                member_id = mem[0]
                full_name = f"{mem[1]} {mem[2]}"
                deg_prog = mem[3]

                # Container frame for label + delete button
                member_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                member_frame.pack(fill="x", padx=10, pady=5)

                # Member label
                member_label = ctk.CTkLabel(member_frame, text=f"{member_id}  |  {full_name}  |  {deg_prog}")
                member_label.pack(side="left", padx=(0, 10))

                # Edit button
                edit_btn = ctk.CTkButton(
                    member_frame,
                    text="Edit",
                    width=30,
                    height=25,
                    fg_color="blue",
                    hover_color="darkblue",
                    text_color="white",
                    font=ctk.CTkFont(size=14),
                    command=lambda m_id=member_id: self.master.show_frame(EditMember, org_id, self.username, m_id)
                )
                edit_btn.pack(side="right")

                # Delete button
                delete_btn = ctk.CTkButton(
                    member_frame,
                    text="x",
                    width=30,
                    height=25,
                    fg_color="red",
                    hover_color="darkred",
                    text_color="white",
                    font=ctk.CTkFont(size=14),
                    command=lambda m_id=member_id, frame=member_frame: self.delete_member(m_id, org_id, frame)
                )
                delete_btn.pack(side="right")
        else:
            ctk.CTkLabel(parent, text="Your organization have no member yet", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        ctk.CTkButton(parent, text="Add Member", command=lambda: self.master.show_frame(AddMember, org_id, self.username)).pack(pady=10)

        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=5)

        search_box = ctk.CTkEntry(search_frame, placeholder_text="Last Name")
        search_box.pack(side="left", padx=(0,5))

        search_result_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_result_frame.pack(side="left", fill="x", expand=True)

        search_btn = ctk.CTkButton(
            search_frame, 
            text="Search", 
            width=40, 
            height=25, 
            fg_color="yellow", 
            hover_color="yellow", 
            text_color="white",
            font=ctk.CTkFont(size=14),
            command=lambda: self.search_member(search_box.get().strip(), org_id, search_result_frame)
            )
        search_btn.pack(side="left", padx=(5,0))

    def search_member(self, last_name, org_id, frame):
        for widget in frame.winfo_children():
            widget.destroy()

        infos = self.db.get_member(last_name, org_id)
        if infos:
            for row in infos:  # Assuming (first_name, last_name)
                member = ctk.CTkLabel(frame, text=f"{row[0]} |  {row[1]} {row[2]}  | username: {row[3]}  |   gender: {row[4]}   |   degree program: {row[5]}")
                member.pack(anchor="w", padx=10, pady=2)
        else:
            ctk.CTkLabel(frame, text="No matching members found.").pack(anchor="w", padx=10)

    def delete_member(self, member_id, org_id, frame):
        if not messagebox.askyesno("Confirm Delete", f"Delete member {member_id}?"):
            return

        self.db.delete_membership(member_id, org_id)  # This should be a method in your StudentOrgDBMS class
        frame.destroy()

    def build_profile_tab(self, parent, org_id, org_name):
        ctk.CTkLabel(parent, text=f"{org_id} | {org_name}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

    def build_event_tab(self, parent, org_id):
        events = self.db.get_org_events(org_id)

        if events:
            scroll_frame = ctk.CTkScrollableFrame(parent, width=300, height=200)
            scroll_frame.pack(pady=10)

            for event in events:
                ctk.CTkLabel(scroll_frame, text=f"{event[1]}").pack(anchor="w", padx=10, pady=5)
        else:
            ctk.CTkLabel(parent, text="Your organization have no event yet", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        ctk.CTkButton(parent, text="Add Events", command=lambda: self.master.show_frame(AddEvent, org_id, self.username)).pack(pady=10)

    def build_payment_tab(self, parent, org_id, username):
        fees = self.db.get_org_fees(org_id)
        if fees:
            scroll_frame = ctk.CTkScrollableFrame(parent, width=600, height=300)
            scroll_frame.pack(pady=10)

            for fee in fees:
                trans_num = fee[0]

                fee_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                fee_frame.pack(fill="x", padx=10, pady=5)

                fee_label = ctk.CTkLabel(fee_frame, text=f"{fee[0]}  |  Amount: {fee[1]}     Due: {fee[2]}   |   From: {fee[3]} {fee[4]}")
                fee_label.pack(side="left", padx=(0, 10))

                edit_btn = ctk.CTkButton(
                        fee_frame,
                        text="Edit",
                        width=30,
                        height=25,
                        fg_color="blue",
                        hover_color="darkblue",
                        text_color="white",
                        font=ctk.CTkFont(size=14),
                        command=lambda f_id=trans_num: self.master.show_frame(UpdateTransaction, org_id, self.username, f_id)
                    )
                edit_btn.pack(side="right")
        else:
            ctk.CTkLabel(parent, text="Your organization have no transaction yet", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        ctk.CTkButton(parent, text="Add Transaction", command=lambda: self.master.show_frame(AddPayment, org_id, username)).pack(pady=10)

class AddMember(ctk.CTkFrame):
    def __init__(self, master, org_id, username):
        super().__init__(master)
        self.org_id = org_id
        self.username = username

        self.db = StudentOrgDBMS()

        ctk.CTkButton(self, text="Go Back", command=lambda: master.show_frame(AdminScreen, username)).pack(pady=10)

        self.addMemberForm()

        ctk.CTkButton(self, text="Add", command=lambda: self.handleAddMem(self.org_id)).pack(pady=10)

    def addMemberForm(self):
        ctk.CTkLabel(self, text="Add New Member", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        self.add_stud_name = ctk.CTkEntry(self, placeholder_text="Name")
        self.add_stud_name.pack(pady=10)

        self.add_stud_num = ctk.CTkEntry(self, placeholder_text="Student Number")
        self.add_stud_num.pack(pady=10)

        self.add_member_status = ctk.CTkOptionMenu(self, values=["ACTIVE", "INACTIVE"])
        self.add_member_status.pack(pady=10)

        self.add_acad_year = ctk.CTkEntry(self, placeholder_text="Academic Year")
        self.add_acad_year.pack(pady=10)

        self.add_classification = ctk.CTkOptionMenu(self, values=["Resident", "Alumn"])
        self.add_classification.pack(pady=10)

        self.add_comm_type = ctk.CTkEntry(self, placeholder_text="Committee")
        self.add_comm_type.pack(pady=10)

        self.add_role = ctk.CTkOptionMenu(self, values=["None","Member","President", "Vice President", "Secretary", "Treasurer", "Head"])
        self.add_role.pack(pady=10)

        self.add_sem = ctk.CTkOptionMenu(self, values=["1", "2", "M"])
        self.add_sem.pack(pady=10)

    def handleAddMem(self, org_id):
        student_num = self.add_stud_num.get().strip()
        membership_status = self.add_member_status.get()
        acad_year = self.add_acad_year.get().strip()
        classification = self.add_classification.get()
        joins_type = self.add_comm_type.get().strip()
        role = self.add_role.get()
        semester = self.add_sem.get()
        role = None if role == "None" else role

        if not joins_type:
            joins_type = None

        # Check if student exist in databases
        if self.db.get_student(student_num):
            self.db.add_membership(student_num, org_id, membership_status, acad_year, classification, joins_type, role, semester)
            self.master.show_frame(AdminScreen, self.username)
        else:
            messagebox.showerror("Failed", "No Student Found")
            return

class EditMember(ctk.CTkFrame):
    def __init__(self, master, org_id, username, student_num):
        super().__init__(master)
        self.org_id = org_id
        self.username = username
        self.student_num = student_num

        self.db = StudentOrgDBMS()

        ctk.CTkButton(self, text="Go Back", command=lambda: master.show_frame(AdminScreen, username)).pack(pady=10)

        ctk.CTkLabel(self, text="Edit Member Details", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        self.editForm()

        ctk.CTkLabel(self, text="Re-enter details if no changes made", font=ctk.CTkFont(size=10, weight="normal")).pack(pady=10)

        ctk.CTkButton(self, text="Submit", command=lambda: self.handEdit(org_id, student_num)).pack(pady=10)

    def editForm(self):
        self.add_member_status = ctk.CTkOptionMenu(self, values=["ACTIVE", "INACTIVE", "EXPELLED", "SUSPENDED"])
        self.add_member_status.pack(pady=10)

        self.add_classification = ctk.CTkOptionMenu(self, values=["Resident", "Alumn"])
        self.add_classification.pack(pady=10)

        self.add_comm_type = ctk.CTkEntry(self, placeholder_text="Committee")
        self.add_comm_type.pack(pady=10)

        self.add_role = ctk.CTkOptionMenu(self, values=["None","Member","President", "Vice President", "Secretary", "Treasurer"])
        self.add_role.pack(pady=10)

    def handEdit(self, org_id, student_num):
        status = self.add_member_status.get()
        classification = self.add_classification.get()
        comm_type = self.add_comm_type.get().strip()
        role = self.add_role.get()
        role = None if role == "None" else role

        if not comm_type:
            comm_type = None

        self.db.editMembership(org_id, student_num, status, classification, comm_type, role)
        self.master.show_frame(AdminScreen, self.username)


class AddEvent(ctk.CTkFrame):
    def __init__(self, master, org_id, username):
        super().__init__(master)
        self.org_id = org_id
        self.username = username

        self.db = StudentOrgDBMS()

        ctk.CTkButton(self, text="Go Back", command=lambda: master.show_frame(AdminScreen, username)).pack(pady=10)

        self.event_name_entry = ctk.CTkEntry(self, placeholder_text="Event Name")
        self.event_name_entry.pack(pady=10)

        ctk.CTkButton(self, text="Submit", command=lambda:
                      (self.db.add_event(org_id, self.event_name_entry.get().strip()), self.master.show_frame(AdminScreen, username))
                      ).pack(pady=10)

class AddPayment(ctk.CTkFrame):
    def __init__(self, master, org_id, username):
        super().__init__(master)
        self.org_id = org_id
        self.username = username

        self.db = StudentOrgDBMS()

        ctk.CTkButton(self, text="Go Back", command=lambda: master.show_frame(AdminScreen, username)).pack(pady=10)

        ctk.CTkLabel(self, text="Create Transaction", font=ctk.CTkFont(size=20)).pack(pady=10)
        self.createFee()

        ctk.CTkButton(self, text="Submit", command=self.handle_createFee).pack(pady=10)

    def createFee(self):
        self.fee_amount_entry = ctk.CTkEntry(self, placeholder_text="Amount in Peso")
        self.fee_amount_entry.pack(pady=10)

        ctk.CTkLabel(self, text="Due Date", font=ctk.CTkFont(size=14)).pack(pady=10)
        self.fee_due_entry = DateEntry(self, width=12, background='darkblue',
                               foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fee_due_entry.pack(pady=10)

        self.payment_status_entry = ctk.CTkOptionMenu(self, values=["PAID", "NOT PAID"])
        self.payment_status_entry.pack(pady=10)

        ctk.CTkLabel(self, text="Payment Date (Leave blank if not paid)", font=ctk.CTkFont(size=14)).pack(pady=10)
        self.pay_date = DateEntry(self, width=12, background='darkblue',
                               foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.pay_date.pack(pady=10)
        self.pay_date.delete(0, 'end')

        self.member_stud_num_entry = ctk.CTkEntry(self, placeholder_text="Student Number")
        self.member_stud_num_entry.pack(pady=10)

    def handle_createFee(self):
            # Check if member exist in the org
        student_num = self.member_stud_num_entry.get().strip()
            
        if self.db.member_exists(student_num, self.org_id):
            self.addFeePayment()
            self.master.show_frame(AdminScreen, self.username)
        else:
            messagebox.showerror("Failed", "No member found!")
            return
            
    def addFeePayment(self):
        stud_num = self.member_stud_num_entry.get().strip()
        amount = self.fee_amount_entry.get().strip()
        due_date = self.fee_due_entry.get()
        payment_status = self.payment_status_entry.get()
        pay_date = self.pay_date.get()

        if not pay_date.strip():
            pay_date = None

        self.trans_num = self.db.add_fee(amount, due_date, self.org_id)

        self.db.add_pays(stud_num, self.trans_num, payment_status, pay_date) 


class UpdateTransaction(ctk.CTkFrame):
    def __init__(self, master, org_id, username, trans_num):
        super().__init__(master)
        self.org_id = org_id
        self.username = username
        self.trans_num = trans_num

        self.db = StudentOrgDBMS()

        ctk.CTkButton(self, text="Go Back", command=lambda: master.show_frame(AdminScreen, username)).pack(pady=10)

        ctk.CTkLabel(self, text="Update Transaction", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        self.updateFee()

        ctk.CTkButton(self, text="Submit", command=lambda: self.handleEditFee(self.trans_num)).pack(pady=10)


    def updateFee(self):
        self.payment_status_entry = ctk.CTkOptionMenu(self, values=["PAID", "NOT PAID"])
        self.payment_status_entry.pack(pady=10)

        ctk.CTkLabel(self, text="Payment Date", font=ctk.CTkFont(size=14)).pack(pady=10)
        self.pay_date = DateEntry(self, width=12, background='darkblue',
                               foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.pay_date.pack(pady=10)
        self.pay_date.delete(0, 'end')

    def handleEditFee(self, trans_num):
        status = self.payment_status_entry.get()
        date = self.pay_date.get()

        if not date or date == "":
            date = None

            messagebox.showerror("Failed", "No date to update when paid!")
            return
        
        self.db.updatePays(status, date, trans_num)
        self.master.show_frame(AdminScreen, self.username)



if __name__ == "__main__":
    app = App() 
    app.mainloop()