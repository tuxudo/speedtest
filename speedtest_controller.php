<?php

/**
 * Speedtest module class
 *
 * @package munkireport
 * @author
 **/
class Speedtest_controller extends Module_controller
{
    /*** Protect methods with auth! ****/
    public function __construct()
    {
        // Store module path
        $this->module_path = dirname(__FILE__);
    }

    /**
     * Default method
     *
     * @author AvB
     **/
    public function index()
    {
        echo "You've loaded the speedtest module!";
    }

    /**
     * Retrieve data in json format
     * @author tuxudo
     *
     **/
    public function get_tab_data($serial_number = '')
    {
        // Remove non-serial number characters
        $serial_number = preg_replace("/[^A-Za-z0-9_\-]/", '', $serial_number);

        $obj = new View();

        if (! $this->authorized()) {
            $obj->view('json', array('msg' => 'Not authorized'));
            return;
        }

        $sql = "SELECT base_rtt, dl_throughput, dl_bytes_transferred, dl_responsiveness, dl_flows, ul_throughput, ul_bytes_transferred, ul_responsiveness, ul_flows, dhcp_domain_name, dhcp_domain_name_servers, dhcp_routers, dhcp_subnet_mask, ipv4ip, ipv4router, ipv4dns, ipv4mask, ipv6ip, ipv6mask, latest, external_ip, external_ip_isp, interface_name, isp, iteration, end_time, country, lat, lon, test_endpoint
                    FROM speedtest 
                    LEFT JOIN reportdata USING (serial_number)
                    ".get_machine_group_filter()."
                    AND serial_number = '$serial_number'";

        $queryobj = new Speedtest_model();
        $speedtest_tab = $queryobj->query($sql);
        $obj->view('json', array('msg' => current(array('msg' => $speedtest_tab)))); 
    }
} // END class Speedtest_controller
