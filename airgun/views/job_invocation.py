from wait_for import wait_for
from widgetastic.widget import Checkbox
from widgetastic.widget import ConditionalSwitchableView
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly import Button

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.views.common import SatTable
from airgun.views.common import SearchableViewMixin
from airgun.widgets import ActionsDropdown
from airgun.widgets import FilteredDropdown
from airgun.widgets import RadioGroup


class JobInvocationsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[contains(., 'Job') and contains(., 'nvocations')]")
    new = Text("//a[contains(@href, '/job_invocations/new')]")
    table = SatTable('.//table', column_widgets={'Description': Text('./a')})

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class JobInvocationCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    job_category = FilteredDropdown(id='job_invocation_job_category')
    job_template = FilteredDropdown(locator="//div[contains(@class, 'job_template_selector')]")
    bookmark = FilteredDropdown(id='targeting_bookmark')
    search_query = TextInput(name='targeting[search_query]')
    template_content = ConditionalSwitchableView(reference='job_template')

    @template_content.register('Run Command - SSH Default', default=True)
    class RunSSHCommandForm(View):
        command = TextInput(id='command')

    @template_content.register('Power Action - SSH Default')
    class RestartHostForm(View):
        action = FilteredDropdown(id='s2id_action')

    @template_content.register('Puppet Run Once - SSH Default')
    class RunPuppetForm(View):
        puppet_options = TextInput(id='puppet_options')

    @template_content.register('Module Action - SSH Default')
    class RunModuleForm(View):
        action = FilteredDropdown(id='s2id_action')
        module_spec = TextInput(id='module_spec')
        puppet_options = TextInput(id='options')

    @View.nested
    class advanced_options(View):
        expander = Text(".//a[normalize-space(.)='Display advanced fields']")
        effective_user = TextInput(locator=".//input[contains(@name, '[effective_user]')]")
        description = TextInput(locator=".//input[contains(@name, '[description]')]")
        use_default = Checkbox(id="description_format_override")
        description_content = ConditionalSwitchableView(reference='use_default')

        @description_content.register(False)
        class DescriptionTemplateForm(View):
            description_template = TextInput(id='job_invocation_description_format')

        timeout = TextInput(locator=".//input[contains(@name, '[execution_timeout_interval]')]")
        password = TextInput(id='job_invocation_password')
        passphrase = TextInput(id='job_invocation_key_passphrase')
        sudo_password = TextInput(id='job_invocation_sudo_password')
        concurrency_level = TextInput(id='job_invocation_concurrency_level')
        time_span = TextInput(id='job_invocation_time_span')
        execution_order = RadioGroup(locator="//div[label[contains(., 'Execution ordering')]]")

        def __init__(self, parent, logger=None):
            """Expand advanced options section once we get to run job page.
            That is need to be able to read or change values there
            """
            View.__init__(self, parent, logger=logger)
            if self.expander.is_displayed:
                self.expander.click()
                self.browser.wait_for_element(self.effective_user, visible=True, exception=False)

    query_type = RadioGroup(locator="//div[label[contains(., 'Type of query')]]")
    schedule = RadioGroup(locator="//div[label[normalize-space(.)='Schedule']]")
    schedule_content = ConditionalSwitchableView(reference='schedule')

    @schedule_content.register('Execute now', default=True)
    class ExecuteNowForm(View):
        pass

    @schedule_content.register('Schedule future execution')
    class FutureExecutionForm(View):
        start_at = TextInput(id='triggering_start_at_raw')
        start_before = TextInput(id='triggering_start_before_raw')

    @schedule_content.register('Set up recurring execution')
    class RecurringExecutionForm(View):
        repeats = FilteredDropdown(id='input_type_selector')
        repeats_content = ConditionalSwitchableView(reference='repeats')

        @repeats_content.register('cronline')
        class CronlineForm(View):
            cron_line = TextInput(id='triggering_cronline')

        @repeats_content.register('monthly')
        class RepeatMonthlyForm(View):
            at_days = TextInput(id='triggering_days')
            at_hours = FilteredDropdown(id='triggering_time_time_4i')
            at_minutes = FilteredDropdown(id='triggering_time_time_5i')

        @repeats_content.register('weekly')
        class RepeatWeeklyForm(View):
            on_mon = Checkbox(id='triggering_days_of_week_1')
            on_tue = Checkbox(id='triggering_days_of_week_2')
            on_wed = Checkbox(id='triggering_days_of_week_3')
            on_thu = Checkbox(id='triggering_days_of_week_4')
            on_fri = Checkbox(id='triggering_days_of_week_5')
            on_sat = Checkbox(id='triggering_days_of_week_6')
            on_sun = Checkbox(id='triggering_days_of_week_7')
            at_hours = FilteredDropdown(id='triggering_time_time_4i')
            at_minutes = FilteredDropdown(id='triggering_time_time_5i')

        @repeats_content.register('daily', default=True)
        class RepeatDailyForm(View):
            at_hours = FilteredDropdown(id='triggering_time_time_4i')
            at_minutes = FilteredDropdown(id='triggering_time_time_5i')

        @repeats_content.register('hourly')
        class RepeatHourlyForm(View):
            at_minutes = FilteredDropdown(id='triggering_time_time_5i')

        repeat_n_times = TextInput(id='triggering_max_iteration')
        ends = RadioGroup(locator="//div[@id='end_time_limit_select']")
        ends_date_content = ConditionalSwitchableView(reference='ends')

        @ends_date_content.register('Never', default=True)
        class NoEndsDateForm(View):
            pass

        @ends_date_content.register('On')
        class EndsDateEnabledForm(View):
            at_year = FilteredDropdown(id='triggering_end_time_end_time_1i')
            at_month = FilteredDropdown(id='triggering_end_time_end_time_2i')
            at_day = FilteredDropdown(id='triggering_end_time_end_time_3i')
            at_hours = FilteredDropdown(id='triggering_end_time_end_time_4i')
            at_minutes = FilteredDropdown(id='triggering_end_time_end_time_5i')

    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Jobs'
            and self.breadcrumb.read() == 'Job invocation'
        )


class JobInvocationStatusView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Jobs'
            and len(self.breadcrumb.locations) == 2
        )

    rerun = Text("//a[normalize-space(.)='Rerun']")
    rerun_failed = Text("//a[normalize-space(.)='Rerun failed']")
    job_task = Text("//a[normalize-space(.)='Job Task']")
    cancel_job = Button(value='Cancel Job')
    abort_job = Button(value='Abort Job')

    @View.nested
    class overview(SatTab):
        job_status = Text(
            "//div[@id='job_invocations_chart_container']"
            "//*[name()='tspan'][contains(@class,'donut-title-small-pf')]"
        )
        job_status_progress = Text(
            "//div[@id='job_invocations_chart_container']"
            "//*[name()='tspan'][contains(@class,'donut-title-big-pf')]"
        )
        execution_order = Text("//p[contains(., 'Execution order:')]")
        hosts_table = SatTable(
            './/table',
            column_widgets={
                'Host': Text('./a'),
                'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
            },
        )
        total_hosts = Text(
            "//h2[contains(., 'Total hosts')]/span[@class='card-pf-aggregate-status-count']"
        )

    def wait_for_result(self, timeout=600, delay=1):
        """Wait for invocation job to finish"""
        wait_for(
            lambda: (
                self.is_displayed
                and self.overview.job_status.is_displayed
                and self.overview.job_status_progress.is_displayed
            ),
            timeout=timeout,
            delay=delay,
            logger=self.logger,
        )
        wait_for(
            lambda: (
                self.overview.job_status.read() != 'Pending'
                and self.overview.job_status_progress.read() == '100%'
            ),
            timeout=timeout,
            delay=1,
            logger=self.logger,
        )
