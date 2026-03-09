/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * sat-spacex-study.cc
 *
 * A VM-friendly version of SNS-3 sat-constellation-example:
 *  - Adds CLI knobs: islRate, simTime, outputTag, fastDev, enableStats, detailedStats
 *  - fastDev=1 reduces flows and disables heavy console printing + heavy stats
 *
 * Put this file in: ns-3.43/scratch/sat-spacex-study.cc
 */


#include "ns3/applications-module.h"
#include "ns3/config-store-module.h"
#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/network-module.h"
#include "ns3/satellite-module.h"
#include "ns3/traffic-module.h"


#include <cstdint>
#include <set>
#include <string>


using namespace ns3;


NS_LOG_COMPONENT_DEFINE("sat-spacex-study");


static NodeContainer
LimitNodes(const NodeContainer& in, uint32_t maxN)
{
  if (maxN == 0 || in.GetN() <= maxN)
    {
      return in;
    }


  NodeContainer out;
  for (uint32_t i = 0; i < maxN; ++i)
    {
      out.Add(in.Get(i));
    }
  return out;
}


int
main(int argc, char* argv[])
{
  // -------------------------
  // CLI parameters (defaults)
  // -------------------------
  uint32_t packetSize = 512;
  std::string interval = "20ms";
  std::string scenarioFolder = "constellation-eutelsat-geo-2-sats-isls";


  // Added knobs
  std::string islRate = "100Mb/s";
  double simTime = 30.0;
  std::string outputTag = "spacex-1600";


  // Performance/output knobs
  bool fastDev = true;        // VM-friendly default
  bool printTopology = false; // huge console output if true
  bool saveAttributes = false; // writes output-attributes.xml if true
  bool enableStats = false;   // minimal stats if true
  bool detailedStats = false; // heavy per-UT stats if true


  // Load reduction knobs (important for speed)
  uint32_t userCountPerUt = 2; // original example uses 2
  uint32_t gwUsersCount = 3;   // original example uses 3
  uint32_t maxGwUsers = 0;     // 0 means all
  uint32_t maxUtUsers = 0;     // 0 means all


  Ptr<SimulationHelper> simulationHelper = CreateObject<SimulationHelper>("spacex-study");


  // -------------------------
  // Command line parsing
  // -------------------------
  CommandLine cmd;
  cmd.AddValue("packetSize", "Size of constant packet (bytes)", packetSize);
  cmd.AddValue("interval", "Interval to send packets (e.g., 50ms, 20ms, 5ms)", interval);
  cmd.AddValue("scenarioFolder", "Scenario folder (e.g. constellation-spacex-1600-sats)", scenarioFolder);


  cmd.AddValue("islRate", "ISL data rate (e.g., 100Mb/s, 500Mb/s, 1Gb/s)", islRate);
  cmd.AddValue("simTime", "Simulation time in seconds", simTime);
  cmd.AddValue("outputTag", "Basename for output directory", outputTag);


  cmd.AddValue("fastDev", "Fast dev mode (disable heavy printing/stats and reduce flows)", fastDev);
  cmd.AddValue("printTopology", "Print topology and ISL map to stdout (slow)", printTopology);
  cmd.AddValue("saveAttributes", "Save output-attributes.xml via ConfigStore (slow)", saveAttributes);
  cmd.AddValue("enableStats", "Enable minimal statistics (some overhead)", enableStats);
  cmd.AddValue("detailedStats", "Enable heavy per-UT statistics (slow)", detailedStats);


  cmd.AddValue("userCountPerUt", "Users per UT (affects load/runtime)", userCountPerUt);
  cmd.AddValue("gwUsersCount", "GW users count (affects load/runtime)", gwUsersCount);
  cmd.AddValue("maxGwUsers", "Limit GW user nodes used for traffic (0=all)", maxGwUsers);
  cmd.AddValue("maxUtUsers", "Limit UT user nodes used for traffic (0=all)", maxUtUsers);


  simulationHelper->AddDefaultUiArguments(cmd);
  cmd.Parse(argc, argv);


  // -------------------------
  // Fast dev defaults
  // -------------------------
  if (fastDev)
    {
      // Disable heavy outputs by default
      printTopology = false;
      saveAttributes = false;
      detailedStats = false;


      // Keep stats OFF unless you explicitly enable them
      enableStats = false;


      // Reduce load unless user already set them
      if (userCountPerUt == 2)
        {
          userCountPerUt = 1;
        }
      if (gwUsersCount == 3)
        {
          gwUsersCount = 1;
        }
      if (maxGwUsers == 0)
        {
          maxGwUsers = 1;
        }
      if (maxUtUsers == 0)
        {
          maxUtUsers = 2;
        }
    }


  // Keep outputs separated (you already added this arg earlier)
  simulationHelper->SetOutputTag(outputTag);


  // -------------------------
  // Core config (based on sat-constellation-example)
  // -------------------------
  Config::SetDefault("ns3::SatConf::ForwardLinkRegenerationMode",
                     EnumValue(SatEnums::REGENERATION_NETWORK));
  Config::SetDefault("ns3::SatConf::ReturnLinkRegenerationMode",
                     EnumValue(SatEnums::REGENERATION_NETWORK));


  Config::SetDefault("ns3::SatOrbiterFeederPhy::QueueSize", UintegerValue(100000));
  Config::SetDefault("ns3::SatOrbiterUserPhy::QueueSize", UintegerValue(100000));


  Config::SetDefault("ns3::PointToPointIslHelper::IslDataRate",
                     DataRateValue(DataRate(islRate)));


  Config::SetDefault("ns3::SatSGP4MobilityModel::UpdatePositionEachRequest", BooleanValue(false));
  Config::SetDefault("ns3::SatSGP4MobilityModel::UpdatePositionPeriod", TimeValue(Seconds(1)));


  Config::SetDefault("ns3::SatHelper::GwUsers", UintegerValue(gwUsersCount));
  Config::SetDefault("ns3::SatGwMac::SendNcrBroadcast", BooleanValue(false));


  Config::SetDefault("ns3::SatHelper::BeamNetworkAddress", Ipv4AddressValue("20.1.0.0"));
  Config::SetDefault("ns3::SatHelper::GwNetworkAddress", Ipv4AddressValue("10.1.0.0"));
  Config::SetDefault("ns3::SatHelper::UtNetworkAddress", Ipv4AddressValue("250.1.0.0"));


  Config::SetDefault("ns3::SatBbFrameConf::AcmEnabled", BooleanValue(true));
  Config::SetDefault("ns3::SatEnvVariables::EnableSimulationOutputOverwrite", BooleanValue(true));


  // Very important for VM performance:
  Config::SetDefault("ns3::SatHelper::PacketTraceEnabled", BooleanValue(false));


  simulationHelper->LoadScenario(scenarioFolder);
  simulationHelper->SetSimulationTime(Seconds(simTime));
  simulationHelper->SetUserCountPerUt(userCountPerUt);


  // Beam set like the original example
  std::set<uint32_t> beamSet = {43, 30};
  std::set<uint32_t> beamSetTelesat = {1, 43, 60, 64};


  if (scenarioFolder == "constellation-telesat-351-sats")
    {
      simulationHelper->SetBeamSet(beamSetTelesat);
    }
  else
    {
      simulationHelper->SetBeamSet(beamSet);
    }


  LogComponentEnable("sat-spacex-study", LOG_LEVEL_INFO);


  // Create the scenario
  simulationHelper->CreateSatScenario();


  // Heavy console printing (OFF by default)
  if (printTopology)
    {
      Singleton<SatTopology>::Get()->PrintTopology(std::cout);
      Singleton<SatIdMapper>::Get()->ShowIslMap();
    }


  // CBR defaults
  Config::SetDefault("ns3::CbrApplication::Interval", StringValue(interval));
  Config::SetDefault("ns3::CbrApplication::PacketSize", UintegerValue(packetSize));


  // Traffic timing: keep inside [0, simTime]
  double startSec = (simTime >= 2.0) ? 1.0 : std::max(0.0, simTime * 0.1);
  double stopSec = std::max(startSec + 0.1, simTime - 0.1);
  if (stopSec > simTime)
    {
      stopSec = simTime;
    }
  if (stopSec <= startSec)
    {
      stopSec = startSec + 0.01;
    }


  Time startTime = Seconds(startSec);
  Time stopTime = Seconds(stopSec);
  Time startDelay = Seconds(0.0);


  // Build traffic endpoints
  NodeContainer uts = Singleton<SatTopology>::Get()->GetUtNodes();
  NodeContainer gwUsers = Singleton<SatTopology>::Get()->GetGwUserNodes();
  NodeContainer utUsers = Singleton<SatTopology>::Get()->GetUtUserNodes(uts);


  // Reduce flow explosion if requested (critical for speed)
  gwUsers = LimitNodes(gwUsers, maxGwUsers);
  utUsers = LimitNodes(utUsers, maxUtUsers);


  Ptr<SatTrafficHelper> trafficHelper = simulationHelper->GetTrafficHelper();


  trafficHelper->AddCbrTraffic(SatTrafficHelper::FWD_LINK,
                               SatTrafficHelper::UDP,
                               Time(interval),
                               packetSize,
                               gwUsers,
                               utUsers,
                               startTime,
                               stopTime,
                               startDelay);


  trafficHelper->AddCbrTraffic(SatTrafficHelper::RTN_LINK,
                               SatTrafficHelper::UDP,
                               Time(interval),
                               packetSize,
                               gwUsers,
                               utUsers,
                               startTime,
                               stopTime,
                               startDelay);


  // Optional: save attributes file (OFF by default)
  if (saveAttributes)
    {
      Config::SetDefault("ns3::ConfigStore::Filename", StringValue("output-attributes.xml"));
      Config::SetDefault("ns3::ConfigStore::FileFormat", StringValue("Xml"));
      Config::SetDefault("ns3::ConfigStore::Mode", StringValue("Save"));
      ConfigStore outputConfig;
      outputConfig.ConfigureDefaults();
    }


  // Statistics: minimal by default, heavy only if detailedStats=1
  if (enableStats)
    {
      Ptr<SatStatsHelperContainer> s = simulationHelper->GetStatisticsContainer();


      // Minimal, known-to-exist stats from the original example
      s->AddGlobalFwdAppThroughput(SatStatsHelper::OUTPUT_SCATTER_FILE);
      s->AddGlobalRtnAppThroughput(SatStatsHelper::OUTPUT_SCATTER_FILE);


      if (detailedStats)
        {
          // These exist in the original example, but can be slow (many files)
          s->AddPerGwFwdAppThroughput(SatStatsHelper::OUTPUT_SCATTER_FILE);
          s->AddPerGwRtnAppThroughput(SatStatsHelper::OUTPUT_SCATTER_FILE);
          s->AddPerUtFwdAppThroughput(SatStatsHelper::OUTPUT_SCATTER_FILE);
          s->AddPerUtRtnAppThroughput(SatStatsHelper::OUTPUT_SCATTER_FILE);
          s->AddPerUtFwdPhyDelay(SatStatsHelper::OUTPUT_SCATTER_FILE);
          s->AddPerUtRtnPhyDelay(SatStatsHelper::OUTPUT_SCATTER_FILE);
        }
    }


  simulationHelper->RunSimulation();
  return 0;
}
